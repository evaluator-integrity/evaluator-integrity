"""Scores the corpus against the criteria and aggregates the results.

TODO(port): the scorer and the aggregation, ported from the lab harness.

Scope note, because this is where the two repositories differ most: the lab
harness scores every stratum. This module publishes individual records for
`framework_default` only -- what a framework ships with by default, which is
already public -- and everything else as an aggregate with no attribution.

`--check` is wired into CI. Once the scorer is ported it must exit non-zero when
a published number cannot be reproduced from the committed corpus, so that a
result drifting away from its evidence breaks the build rather than sitting
there looking authoritative.
"""

from __future__ import annotations

import argparse
import sys

NOT_YET_PORTED = (
    "conformance.report: scoring and aggregation are not yet ported "
    "(TODO(port) in conformance/report.py)."
)


def check() -> int:
    """Re-derive every published figure from the committed corpus."""
    print(NOT_YET_PORTED)
    print(
        "Nothing has been scored, so there is nothing to contradict. This exits 0\n"
        "because an unported module is not a regression -- but it is also not a\n"
        "passing test, and it must not be read as one."
    )
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument(
        "--check",
        action="store_true",
        help="verify published results still follow from the committed corpus",
    )
    args = parser.parse_args(argv)

    if args.check:
        return check()

    parser.print_help()
    return 0


if __name__ == "__main__":
    sys.exit(main())
