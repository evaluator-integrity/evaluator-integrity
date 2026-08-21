"""Checks the citation chain: every claim in the criteria tied to a source.

    python -m conformance.verify_citations                # the ledger
    python -m conformance.verify_citations --check        # CI
    python -m conformance.verify_citations --require-sources
    python -m conformance.verify_citations --json

This is the criteria-level counterpart to `verify_quotes.py`. That module ties a
corpus verdict to the bytes of a shipped package; this ties a criterion to the
published result it claims to rest on.

What runs in CI, and what it can fail on
----------------------------------------
Everything here runs on a bare clone with no network and no papers. It fails on:

  * a numeral stated in the criteria with no entry in the ledger -- the property
    that was missing, and the reason a figure could be written into a rationale
    with nothing anywhere asking where it came from;
  * a `supports` span that is no longer a substring of the criterion text --
    the criterion has been edited away from its evidence;
  * a declared numeral that is no longer in the criterion text -- the ledger has
    been left behind by an edit;
  * a verified claim whose quote does not contain the numeral it is offered for;
  * a claim naming a source that does not exist, or a source with no pinned
    identifier.

It does NOT fail on unverified claims. Most of this ledger is unverified, and
failing the build for it would mean either a permanently red build or deleting
the entries, and the entries are the finding. They are counted and printed
instead, every run, so the number is in front of anyone who looks.

`--require-sources` turns unverified and unsupported into failures. That is the
mode for publishing a criteria version, where a rationale resting on figures
nobody has read back out of the source is not acceptable. It is the same
distinction `verify_quotes.py --require-artifacts` draws, for the same reason:
a run that verified nothing must never look like a run where verification
passed.
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter

from conformance.citations import (CITED_FIELDS, CLAIMS, SOURCES,
                                   SOURCES_BY_ID, STATUSES, numerals)
from conformance.criteria import CRITERIA, CRITERIA_BY_ID

# A source is pinned if its identifier fixes WHICH bytes. An arXiv id with a
# version does; a bare arXiv id does not, because v2 may say something else.
# A dated document is the weaker fallback and is accepted, and named as weaker
# in the report rather than treated as equivalent.
def pinning(identifier: str) -> str:
    if "arxiv:" in identifier.lower():
        return "version" if "v" in identifier.rsplit(".", 1)[-1] else "none"
    return "date" if any(c.isdigit() for c in identifier) else "none"


def check() -> list[str]:
    problems = []

    for s in SOURCES:
        if pinning(s.identifier) == "none":
            problems.append(
                f"source {s.id}: identifier {s.identifier!r} does not pin a "
                f"version or a date. A citation that can be revised under the "
                f"reader is not evidence.")

    for i, c in enumerate(CLAIMS):
        where = f"claim {i} ({c.criterion_id}/{c.field})"
        crit = CRITERIA_BY_ID.get(c.criterion_id)
        if crit is None:
            problems.append(f"{where}: unknown criterion {c.criterion_id!r}")
            continue
        if c.field not in CITED_FIELDS:
            problems.append(f"{where}: field {c.field!r} not in {CITED_FIELDS}")
            continue
        if c.status not in STATUSES:
            problems.append(f"{where}: status {c.status!r} not in {STATUSES}")
            continue
        if c.source not in SOURCES_BY_ID:
            problems.append(f"{where}: unknown source {c.source!r}")

        text = getattr(crit, c.field)

        if not c.supports:
            problems.append(
                f"{where}: no supports span. A claim that names no text in the "
                f"criterion cannot be broken by editing that text, which is "
                f"the whole point of recording it.")
        for span in c.supports:
            if span not in text:
                problems.append(
                    f"{where}: SPAN NOT FOUND in {c.field}\n      {span[:110]!r}"
                    f"\n      The criterion has been edited away from the "
                    f"evidence recorded for it. Either the edit is wrong or "
                    f"this entry is stale; both need a person.")

        for n in c.numbers:
            if n not in numerals(text):
                problems.append(
                    f"{where}: declares {n!r}, which is no longer stated in "
                    f"{c.field}. The ledger has been left behind by an edit.")

        if c.status == "unverified":
            if c.quote:
                problems.append(
                    f"{where}: status is unverified but a quote is recorded. "
                    f"An unread span has no quote; recording one asserts a "
                    f"verification that did not happen.")
        else:
            if not c.quote:
                problems.append(f"{where}: status {c.status!r} needs a quote.")
            if not c.locator:
                problems.append(
                    f"{where}: status {c.status!r} needs a locator. A quote "
                    f"nobody can find again is not re-checkable.")

        # Only for `verified`. An `unsupported` claim's quote is what the
        # source says INSTEAD of the criterion, so it is expected not to
        # contain the figure the criterion states -- that is the finding.
        if c.status == "verified":
            for n in c.numbers:
                if n not in c.quote:
                    problems.append(
                        f"{where}: verified for {n!r}, but the quote does not "
                        f"contain it. A quote that does not state the figure "
                        f"is not evidence for the figure.")

    for crit in CRITERIA:
        for field in CITED_FIELDS:
            stated = numerals(getattr(crit, field))
            declared = {n for c in CLAIMS
                        if c.criterion_id == crit.id and c.field == field
                        for n in c.numbers}
            for n in sorted(stated - declared):
                problems.append(
                    f"{crit.id}/{field}: states {n!r} with no entry in the "
                    f"citation ledger. Every quantity the criteria state must "
                    f"name the source it came from, even if nobody has read it "
                    f"back out yet. Add a Claim -- status 'unverified' is an "
                    f"honest value.")

    return problems


def summarise() -> dict:
    by_status = Counter(c.status for c in CLAIMS)
    stated = sum(len(numerals(getattr(c, f)))
                 for c in CRITERIA for f in CITED_FIELDS)
    return {
        "claims": len(CLAIMS),
        "verified": by_status["verified"],
        "unsupported": by_status["unsupported"],
        "unverified": by_status["unverified"],
        "sources": len(SOURCES),
        "numerals_stated": stated,
        "criteria_with_no_verified_claim": sorted(
            c.id for c in CRITERIA
            if not any(cl.criterion_id == c.id and cl.status == "verified"
                       for cl in CLAIMS)),
    }


def render(summary: dict) -> None:
    print("Citation chain\n")
    for s in SOURCES:
        mark = {"version": "pinned", "date": "dated only", "none": "UNPINNED"}
        print(f"  {s.id:20s} {s.identifier:28s} {mark[pinning(s.identifier)]}")
    print()
    print(f"  claims        {summary['claims']}")
    print(f"    verified    {summary['verified']}")
    print(f"    unsupported {summary['unsupported']}")
    print(f"    unverified  {summary['unverified']}")
    print(f"  numerals stated in the criteria: {summary['numerals_stated']}, "
          f"all declared")
    print()

    for c in CLAIMS:
        if c.status == "unsupported":
            print(f"  UNSUPPORTED  {c.criterion_id}/{c.field}  "
                  f"[{c.source} {c.locator}]")
            print(f"    criterion says: {c.supports[0][:100]}")
            print(f"    source says:    {c.quote[:100]}")
    blind = summary["criteria_with_no_verified_claim"]
    if blind:
        print(f"  NO VERIFIED CLAIM AT ALL: {', '.join(blind)}")
        print("    Every quantity in these criteria is stated on the strength "
              "of a citation nobody has read back out.")
    if summary["unverified"]:
        print(f"\n  {summary['unverified']} of {summary['claims']} claims are "
              f"unverified. This is NOT a pass. Run with --require-sources "
              f"before publishing a criteria version.")


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--check", action="store_true",
                   help="accepted for symmetry with the other conformance "
                        "entry points; checking is the default action. It must "
                        "remain ACCEPTED: without it a caller passing it exits "
                        "2 on an argparse error, which is 'the check could not "
                        "run' and must never be read as a pass.")
    p.add_argument("--require-sources", action="store_true",
                   help="turn unverified and unsupported claims into failures; "
                        "use this when publishing a criteria version")
    p.add_argument("--json", action="store_true")
    args = p.parse_args(argv)

    problems = list(check())
    summary = summarise()

    if args.require_sources:
        for c in CLAIMS:
            if c.status != "verified":
                problems.append(
                    f"{c.criterion_id}/{c.field} [{c.source}]: status is "
                    f"{c.status!r}. --require-sources was passed, so a claim "
                    f"that has not been read back out of the pinned source is "
                    f"a failure. Read it, or remove the claim from the "
                    f"criteria.")

    if args.json:
        print(json.dumps({**summary, "problems": problems}, indent=2))
    else:
        render(summary)

    if problems:
        print(f"\n{len(problems)} PROBLEM(S):\n", file=sys.stderr)
        for pr in problems:
            print("  -", pr, file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
