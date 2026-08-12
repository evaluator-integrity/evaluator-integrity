"""Executable form of the Evaluator Integrity criteria.

The criteria are published as prose in `criteria/vX.Y/index.md`. This package is
the machine-readable counterpart: the same criteria as data, the scorer that
applies them to the corpus, and the checks that let a reader re-verify a
published result instead of taking it on trust.

The prose is normative. Where this package and the published criteria text
disagree, the text wins and the package has a bug.
"""

__all__ = ["criteria", "provenance", "report", "verify_quotes"]

# Version of the criteria this package implements. Tracks the criteria
# directory (criteria/v0.1/), not the Python distribution.
CRITERIA_VERSION = "0.1"
