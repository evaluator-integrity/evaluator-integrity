#!/usr/bin/env python3
"""Refuse to let private material enter the public Evaluator Integrity repository.

This repository will be made public. When that happens it does not publish its
current state -- it publishes its entire history. A file that is committed today
and deleted tomorrow is still readable by anyone who clones the repository, for
as long as the repository exists. There is no undo.

This script is the last automated thing standing between the private research
material and that permanent record. It runs in two places, and the difference
matters:

  * as a pre-commit hook  -- prevents the bad commit from ever existing.
  * as a CI step          -- catches a leak that is *already in history*, at
                             which point the fix is no longer "git commit
                             --amend", it is rotating whatever leaked and
                             rewriting or abandoning the branch.

The hook is the one that saves you. CI is the alarm that tells you it is too
late for the cheap fix.

If this script fails, the fix is to remove the offending material -- never to
weaken the check, add an exclusion, or pass --no-verify. A check that has been
taught to ignore the thing it exists to catch is worse than no check, because it
still reads as protection.

Usage
    python scripts/check_public_safe.py            # scan the whole working tree
    python scripts/check_public_safe.py --staged   # scan what is staged (hook)

Exit codes
    0  nothing private found
    1  private material found -- read the report, do not bypass
    2  the check could not run (missing denylist, git failure); treated as a
       failure, because "the guard could not run" must never look like "clean".
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import textwrap
from dataclasses import dataclass
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
DENYLIST_PATH = REPO_ROOT / "scripts" / "denylist.txt"

# Top-level directories that belong to evaluator-integrity-lab and have no home
# here. Matched at any depth, so `notes/strategy/` trips as well as `strategy/`.
FORBIDDEN_DIR_NAMES = (
    "demo",
    "search",
    "harness",
    "outreach",
    "strategy",
    "corpus-private",
)

# The only corpus stratum that may be published as individual records.
PUBLISHABLE_STRATUM = "framework_default"

# Fields that mark a record as belonging to a specific engagement.
FORBIDDEN_RECORD_FIELDS = ("client", "engagement")

# Files the content scans must not read, or they would match themselves.
SELF_EXEMPT = (
    "scripts/denylist.txt",
    "scripts/check_public_safe.py",
)

RECORD_SUFFIXES = (".json", ".jsonl")

# Anything under a directory named `corpus` is treated as corpus data.
CORPUS_DIR_NAME = "corpus"

BINARY_SNIFF_BYTES = 8000


@dataclass(frozen=True)
class Finding:
    """One reason this repository is not safe to publish."""

    heading: str
    path: str
    detail: str
    why: str
    fix: str


# --------------------------------------------------------------------------
# Reading the tree
# --------------------------------------------------------------------------


def _git(*args: str) -> str:
    result = subprocess.run(
        ["git", *args],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise RuntimeError(f"git {' '.join(args)} failed: {result.stderr.strip()}")
    return result.stdout


def list_paths(staged: bool) -> list[str]:
    """Repository-relative paths to scan, as forward-slash strings."""
    if staged:
        # Only what is about to be committed. Deletions are irrelevant here.
        out = _git("diff", "--cached", "--name-only", "--diff-filter=ACMR", "-z")
    else:
        # Tracked files plus untracked-but-not-ignored files. Ignored paths are
        # excluded because they cannot be committed, which is the whole point.
        out = _git("ls-files", "--cached", "--others", "--exclude-standard", "-z")
    return [p for p in out.split("\0") if p]


def read_bytes(path: str, staged: bool) -> bytes | None:
    """Content of `path`. In staged mode this is the staged blob, not the file
    on disk -- they can differ, and the staged blob is what gets committed."""
    if staged:
        result = subprocess.run(
            ["git", "show", f":{path}"],
            cwd=REPO_ROOT,
            capture_output=True,
        )
        return result.stdout if result.returncode == 0 else None
    try:
        return (REPO_ROOT / path).read_bytes()
    except (OSError, ValueError):
        return None


def is_binary(blob: bytes) -> bool:
    return b"\0" in blob[:BINARY_SNIFF_BYTES]


def decode(blob: bytes) -> str:
    return blob.decode("utf-8", errors="replace")


# --------------------------------------------------------------------------
# Check 1 -- forbidden paths
# --------------------------------------------------------------------------


def check_paths(paths: list[str]) -> list[Finding]:
    findings = []
    for path in paths:
        parts = Path(path).parts[:-1]  # directories only, not the filename
        for part in parts:
            if part.lower() in FORBIDDEN_DIR_NAMES:
                findings.append(
                    Finding(
                        heading="Private directory",
                        path=path,
                        detail=f"sits under a directory named '{part}/'",
                        why=(
                            f"'{part}/' is lab material. The search harness, demo "
                            "assets, outreach and strategy documents live in "
                            "evaluator-integrity-lab and are never published. Every "
                            "artefact has exactly one home; if this file exists in "
                            "both repositories, that is a defect."
                        ),
                        fix=(
                            "Delete it here. If the work needs to move between "
                            "repositories, Idil moves it by hand, deliberately, in "
                            "one direction."
                        ),
                    )
                )
                break
    return findings


# --------------------------------------------------------------------------
# Check 2 & 3 -- corpus records
# --------------------------------------------------------------------------


def is_corpus_record(path: str) -> bool:
    p = Path(path)
    if p.suffix.lower() not in RECORD_SUFFIXES:
        return False
    if p.name.startswith("_"):
        # Templates and schemas (_TEMPLATE.json) describe records; they are not
        # records. They are still subject to the path and denylist checks.
        return False
    return CORPUS_DIR_NAME in {part.lower() for part in p.parts[:-1]}


def _iter_records(text: str, path: str) -> tuple[list[object], str | None]:
    """Return (records, parse_error). Handles both .json and .jsonl."""
    if path.lower().endswith(".jsonl"):
        records: list[object] = []
        for lineno, line in enumerate(text.splitlines(), start=1):
            line = line.strip()
            if not line:
                continue
            try:
                records.append(json.loads(line))
            except json.JSONDecodeError as exc:
                return [], f"line {lineno}: {exc.msg}"
        return records, None
    try:
        parsed = json.loads(text)
    except json.JSONDecodeError as exc:
        return [], f"line {exc.lineno}: {exc.msg}"
    return (parsed if isinstance(parsed, list) else [parsed]), None


def _walk_dicts(node: object):
    """Yield every dict anywhere in a decoded JSON structure, so a record
    nested inside a wrapper object cannot slip past the field checks."""
    if isinstance(node, dict):
        yield node
        for value in node.values():
            yield from _walk_dicts(value)
    elif isinstance(node, list):
        for value in node:
            yield from _walk_dicts(value)


def check_records(path: str, text: str) -> list[Finding]:
    findings = []
    records, parse_error = _iter_records(text, path)

    if parse_error is not None:
        return [
            Finding(
                heading="Unreadable corpus record",
                path=path,
                detail=f"is not valid JSON ({parse_error})",
                why=(
                    "A record this check cannot parse is a record it cannot clear. "
                    "An unverifiable file is treated as unsafe, not as absent."
                ),
                fix="Fix the JSON so the stratum and field checks can run.",
            )
        ]

    for record in records:
        for obj in _walk_dicts(record):
            keys = {k.lower(): k for k in obj}

            for field in FORBIDDEN_RECORD_FIELDS:
                if field in keys:
                    findings.append(
                        Finding(
                            heading="Engagement material in a corpus record",
                            path=path,
                            detail=f"contains a '{keys[field]}' field",
                            why=(
                                "A record carrying a client or engagement field "
                                "identifies whose evaluator was audited. That "
                                "belongs to the engagement, not to the published "
                                "standard, and publishing it would breach the "
                                "expectation the work was done under."
                            ),
                            fix=(
                                "Remove the field. If the finding matters publicly, "
                                "publish it as an aggregate with no attribution."
                            ),
                        )
                    )

            if "stratum" in keys:
                value = obj[keys["stratum"]]
                if value != PUBLISHABLE_STRATUM:
                    findings.append(
                        Finding(
                            heading="Non-publishable corpus stratum",
                            path=path,
                            detail=f"has stratum '{value}'",
                            why=(
                                f"Only '{PUBLISHABLE_STRATUM}' records may be "
                                "published individually. They describe what a "
                                "framework ships with out of the box, which is "
                                "already public. Every other stratum describes an "
                                "individual organisation's own configuration and is "
                                "reportable in aggregate only."
                            ),
                            fix=(
                                "Keep the record in evaluator-integrity-lab and "
                                "publish only the aggregate derived from it."
                            ),
                        )
                    )

    # Fail closed: a record whose stratum cannot be determined has not been
    # shown to be publishable, and "not shown to be safe" is not "safe".
    for record in records:
        if isinstance(record, dict) and not any(
            k.lower() == "stratum" for k in record
        ):
            findings.append(
                Finding(
                    heading="Corpus record with no stratum",
                    path=path,
                    detail="has no 'stratum' field",
                    why=(
                        "Publishability is decided by stratum. A record without one "
                        "cannot be cleared, so it is refused rather than assumed "
                        "safe."
                    ),
                    fix=(
                        f"Add \"stratum\": \"{PUBLISHABLE_STRATUM}\" if that is what "
                        "it is. If it is not, it does not belong in this repository."
                    ),
                )
            )

    return findings


# --------------------------------------------------------------------------
# Check 4 -- denylist
# --------------------------------------------------------------------------


def load_denylist() -> list[str]:
    if not DENYLIST_PATH.exists():
        raise RuntimeError(
            f"{DENYLIST_PATH.relative_to(REPO_ROOT)} is missing. It is part of the "
            "guard, not an optional extra; without it the denylist check silently "
            "passes everything. Restore it from git history."
        )
    terms = []
    for line in DENYLIST_PATH.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line and not line.startswith("#"):
            terms.append(line)
    return terms


def _normalise(value: str) -> str:
    """Collapse every run of non-alphanumeric characters to a single space.

    So a denylisted 'Acme Corp' also matches 'acme-corp.json', 'acme_corp' and
    'Acme.Corp'. Slugified filenames are exactly how a client name reaches a
    repository by accident, and a denylist that misses them is a guard with a
    hole in the shape of the thing it was written to catch.
    """
    return re.sub(r"[^a-z0-9]+", " ", value.lower())


def check_denylist(path: str, text: str | None, terms: list[str]) -> list[Finding]:
    findings = []
    haystacks = [("path", path.lower(), _normalise(path))]
    if text is not None:
        haystacks.append(("contents", text.lower(), _normalise(text)))

    for term in terms:
        needle = term.lower()
        needle_normalised = _normalise(term)
        for where, haystack, haystack_normalised in haystacks:
            if needle in haystack or (
                needle_normalised and needle_normalised in haystack_normalised
            ):
                findings.append(
                    Finding(
                        heading="Denylisted string",
                        path=path,
                        detail=f"{where} contain '{term}'",
                        why=(
                            "This string is on scripts/denylist.txt, which means "
                            "someone decided it identifies material that must not be "
                            "published from this repository."
                        ),
                        fix=(
                            "Remove the string. Only remove the denylist entry itself "
                            "if the reason it was added no longer holds -- and say so "
                            "in the commit message."
                        ),
                    )
                )
                break
    return findings


# --------------------------------------------------------------------------
# Reporting
# --------------------------------------------------------------------------


def _wrap(label: str, body: str) -> str:
    """Wrap an explanation to terminal width. Whoever reads this is in a hurry;
    a paragraph running off the right edge is a paragraph that gets skipped."""
    return textwrap.fill(
        f"{label} {body}",
        width=74,
        initial_indent="  ",
        subsequent_indent="    ",
    )


def report(findings: list[Finding], staged: bool) -> None:
    print()
    print("=" * 74)
    print(" PUBLIC-SAFETY CHECK FAILED")
    print("=" * 74)
    print()
    print(
        "This repository is public, or will be. Publishing it publishes its whole\n"
        "history -- not just its current state. Deleting a file in a later commit\n"
        "does not unpublish it."
    )
    print()

    grouped: dict[str, list[Finding]] = {}
    for finding in findings:
        grouped.setdefault(finding.heading, []).append(finding)

    for heading, items in grouped.items():
        print(f"-- {heading} " + "-" * max(0, 71 - len(heading)))
        print()
        seen_paths = set()
        for item in items:
            key = (item.path, item.detail)
            if key in seen_paths:
                continue
            seen_paths.add(key)
            print(f"  {item.path}")
            print(f"      {item.detail}")
        print()
        print(_wrap("Why this matters:", items[0].why))
        print()
        print(_wrap("What to do:", items[0].fix))
        print()

    print("=" * 74)
    if staged:
        print(
            "Nothing has been committed. Fix the files above and stage them again.\n"
            "\n"
            "Do not pass --no-verify. Do not add an exclusion to this check. The\n"
            "check is not the problem; it is doing the one job it exists to do, and\n"
            "the commit it is refusing is the kind that cannot be taken back."
        )
    else:
        print(
            "This material is already in the working tree, and may already be in\n"
            "history. Check with:\n"
            "\n"
            "    git log --oneline --all -- <path>\n"
            "\n"
            "If it has been committed, removing it now is not enough -- it stays in\n"
            "history. Treat anything sensitive in it as disclosed and rotate it.\n"
            "Weakening this check is never the fix."
        )
    print("=" * 74)
    print()


# --------------------------------------------------------------------------


def run(staged: bool) -> int:
    try:
        terms = load_denylist()
        paths = list_paths(staged)
    except RuntimeError as exc:
        print(f"check_public_safe: cannot run: {exc}", file=sys.stderr)
        print(
            "Treating this as a failure. A guard that could not run must never be\n"
            "mistaken for a guard that found nothing.",
            file=sys.stderr,
        )
        return 2

    findings: list[Finding] = []
    findings.extend(check_paths(paths))

    for path in paths:
        if path in SELF_EXEMPT:
            continue

        blob = read_bytes(path, staged)
        if blob is None:
            continue

        text = None if is_binary(blob) else decode(blob)

        findings.extend(check_denylist(path, text, terms))

        if text is not None and is_corpus_record(path):
            findings.extend(check_records(path, text))

    if findings:
        report(findings, staged)
        return 1

    scope = "staged changes" if staged else "working tree"
    print(f"check_public_safe: {len(paths)} files scanned in the {scope}; clean.")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Refuse private material entry to the public repository."
    )
    parser.add_argument(
        "--staged",
        action="store_true",
        help="scan staged content instead of the working tree (pre-commit hook mode)",
    )
    args = parser.parse_args()
    return run(staged=args.staged)


if __name__ == "__main__":
    sys.exit(main())
