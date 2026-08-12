"""Re-verifies that every evidence quote still appears in the artifact it cites.

A corpus record quotes the source it was scored from. A quote is only evidence
if it is still there, unaltered, in the pinned artifact -- otherwise it is a
claim about something the reader cannot inspect. This module reads the quotes
back out of the artifact tree, checks each file's SHA-256 against the recorded
digest, and fails on anything that no longer matches.

THE ARTIFACT TREE IS NOT IN THIS REPOSITORY. It is large and rebuildable from
public package registries; `--how` prints the commands. So this check cannot run
on a bare clone, and CI runs without it.

That absence is handled explicitly rather than quietly. When the artifact tree
is missing this exits 0, but it announces the skip and emits a CI warning
annotation, so a run with no verification never looks the same as a run where
verification passed. Pass --require-artifacts to turn the skip into a failure;
that is the mode for publishing a criteria version, where unverified evidence is
not acceptable.

Point it at the artifact tree with $EVALINT_ARTIFACTS or --artifacts.

A digest mismatch is not necessarily an error on our side: it means the vendor
shipped different bytes. That is a finding. It is never a reason to loosen the
check.
"""

from __future__ import annotations

import argparse
import hashlib
import os
import sys
from pathlib import Path

from conformance.provenance import ARTIFACTS, ARTIFACTS_BY_CONFIG
from conformance.report import load_corpus

ARTIFACTS_ENV_VAR = "EVALINT_ARTIFACTS"
DEFAULT_ARTIFACTS_DIR = "artifacts"

HOW = """\
Rebuild the artifact tree from the public registries, then point this at it.

    mkdir -p artifacts && cd artifacts
    for p in ragas==0.4.3 autoevals==0.3.0 langchain-classic==1.0.8 \\
             arize-phoenix-evals==3.3.0 arize-phoenix-evals==2.0.0 \\
             openevals==0.2.0 mlflow==3.15.1 evals deepeval==4.1.5; do
        pip download --no-deps --dest . "$p"
    done
    mkdir -p x
    for w in *.whl; do d="x/${w%%-*}"; mkdir -p "$d"; unzip -oq "$w" -d "$d"; done
    unzip -oq arize_phoenix_evals-2.0.0-*.whl -d x/phoenix200
    npm pack promptfoo@0.122.0
    mkdir -p x/promptfoo && tar -xzf promptfoo-0.122.0.tgz -C x/promptfoo

    EVALINT_ARTIFACTS=artifacts/x python -m conformance.verify_quotes

DeepEval is read from the installed package, so `pip install deepeval==4.1.5`
must also be in effect.
"""


def resolve_artifacts(explicit: str | None) -> Path:
    if explicit:
        return Path(explicit).expanduser()
    if os.environ.get(ARTIFACTS_ENV_VAR):
        return Path(os.environ[ARTIFACTS_ENV_VAR]).expanduser()
    return Path(DEFAULT_ARTIFACTS_DIR)


def announce_skip(artifacts: Path, require: bool) -> int:
    message = (
        f"evidence quotes were NOT verified: no artifact tree at '{artifacts}'"
    )
    if os.environ.get("GITHUB_ACTIONS"):
        print(f"::warning title=Quotes not verified::{message}")
    banner = "!" * 74
    stream = sys.stderr if require else sys.stdout
    print(banner, file=stream)
    print(f"  SKIPPED: {message}", file=stream)
    print(banner, file=stream)
    if require:
        print("  --require-artifacts was passed, so this is a failure.",
              file=stream)
        return 1
    print("  Run with --how to rebuild the tree. This is NOT a pass.")
    return 0


def resolve(art, root: str) -> str:
    if art.package.startswith("deepeval"):
        import deepeval
        return os.path.join(os.path.dirname(deepeval.__file__),
                            art.path.split("/", 1)[1])
    top = {"ragas": "ragas", "evals": "evals", "autoevals": "autoevals",
           "langchain-classic": "langchain_classic", "openevals": "openevals",
           "mlflow": "mlflow", "promptfoo": "promptfoo"}
    name = art.package.split("==")[0].split("@")[0]
    if name == "arize-phoenix-evals":
        stem = "phoenix200" if "2.0.0" in art.package else "arize_phoenix_evals"
    else:
        stem = top.get(name, name)
    return os.path.join(root, stem, art.path)

def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    # Verification is the default action here. --check is accepted because it is
    # the invocation CI and criteria/README.md step 3 already use, and because
    # `conformance.report --check` means the same thing. Dropping it would turn
    # both documented commands into argparse errors, which exit 2 and read as
    # "the check failed to run" -- the one outcome this repository must never
    # confuse with "the check passed".
    p.add_argument("--check", action="store_true",
                   help="re-verify every evidence quote (the default action; "
                        "accepted so the documented invocation keeps working)")
    p.add_argument("--artifacts", default=None)
    p.add_argument("--require-artifacts", action="store_true",
                   help="turn a missing artifact tree into a failure; use this "
                        "when publishing a criteria version")
    p.add_argument("--how", action="store_true",
                   help="print the commands that rebuild the artifact tree")
    p.add_argument("--corpus", default="conformance/corpus")
    args = p.parse_args(argv)

    if args.how:
        print(HOW)
        return 0

    root = resolve_artifacts(args.artifacts)
    if not root.exists():
        return announce_skip(root, args.require_artifacts)

    failures, checked = [], 0
    for art in ARTIFACTS:
        path = resolve(art, str(root))
        label = f"{art.package}:{art.path}"
        if not os.path.exists(path):
            failures.append(f"{label}: artifact not found at {path}. "
                            f"Run --how to rebuild the tree.")
            continue
        raw = open(path, "rb").read()
        checked += 1
        digest = hashlib.sha256(raw).hexdigest()
        if digest != art.sha256:
            failures.append(
                f"{label}: DIGEST CHANGED\n      recorded {art.sha256}\n"
                f"      actual   {digest}\n"
                f"      The vendor shipped different bytes. Re-read the file "
                f"before publishing anything that cites it.")
        text = raw.decode("utf-8", "replace")
        for frag in art.fragments:
            if frag not in text:
                failures.append(
                    f"{label}: FRAGMENT NOT FOUND\n      {frag[:110]!r}\n"
                    f"      The quoted sentence is no longer in the shipped "
                    f"artifact. The record citing it is stale.")

    records = load_corpus(args.corpus)
    unbacked = [r["config_id"] for r in records
                if r["config_id"] not in ARTIFACTS_BY_CONFIG]
    for cid in unbacked:
        failures.append(f"{cid}: no artifact backs this record. Every verdict "
                        f"must be traceable to downloadable bytes.")

    print(f"artifacts checked: {checked}/{len(ARTIFACTS)}")
    print(f"corpus records:    {len(records)}, {len(records) - len(unbacked)} backed")

    if failures:
        print(f"\n{len(failures)} PROBLEM(S):\n", file=sys.stderr)
        for f in failures:
            print("  -", f, file=sys.stderr)
        return 1
    print("\nAll evidence verified against shipped artifacts.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
