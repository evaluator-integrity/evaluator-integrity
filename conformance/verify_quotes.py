"""Re-verifies that every evidence quote still appears in the artifact it cites.

TODO(port): the quote re-verification itself, ported from the lab harness.

A corpus record quotes the source it was scored from. A quote is only evidence
if it is still there, unaltered, in the pinned artifact -- otherwise it is a
claim about something the reader cannot inspect. This module reads the quotes
back out of the artifact tree and fails on any that no longer match.

THE ARTIFACT TREE IS NOT IN THIS REPOSITORY. It is large, and it contains
material from strata that are not publishable. So this check cannot run on a
bare clone, and CI runs without it.

That absence is handled explicitly rather than quietly. When the artifact tree
is missing this exits 0, but it announces the skip and emits a CI warning
annotation, so a run with no verification never looks the same as a run where
verification passed. Pass --require-artifacts to turn the skip into a failure;
that is the mode for publishing a criteria version, where unverified evidence is
not acceptable.

Point it at the artifact tree with $EVALINT_ARTIFACTS or --artifacts.
"""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

ARTIFACTS_ENV_VAR = "EVALINT_ARTIFACTS"
DEFAULT_ARTIFACTS_DIR = "artifacts"


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
        # Surfaces in the CI summary, so a green run still shows the gap.
        print(f"::warning title=Quotes not verified::{message}")

    banner = "!" * 74
    stream = sys.stderr if require else sys.stdout
    print(banner, file=stream)
    print(f"  SKIPPED: {message}", file=stream)
    print(banner, file=stream)
    print(
        f"\nThe artifact tree is not committed here. Set ${ARTIFACTS_ENV_VAR} or pass\n"
        "--artifacts to verify against a local copy.\n",
        file=stream,
    )

    if require:
        print(
            "--require-artifacts was set, so this is a failure. Evidence that has\n"
            "not been re-verified must not be published.",
            file=stream,
        )
        return 1

    print(
        "Exiting 0: this run made no claim about the quotes. It did not check them\n"
        "and it did not pass them. Do not treat a green build as verified evidence\n"
        "unless this check actually ran."
    )
    return 0


def verify(artifacts: Path) -> int:
    """Re-read every quoted span out of the pinned artifacts."""
    print(f"conformance.verify_quotes: artifact tree found at '{artifacts}'.")
    print(
        "TODO(port): quote re-verification is not yet ported "
        "(conformance/verify_quotes.py). Nothing was verified."
    )
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument(
        "--check",
        action="store_true",
        help="re-verify every evidence quote against its pinned artifact",
    )
    parser.add_argument(
        "--artifacts",
        metavar="DIR",
        help=f"path to the artifact tree (default: ${ARTIFACTS_ENV_VAR} or ./{DEFAULT_ARTIFACTS_DIR})",
    )
    parser.add_argument(
        "--require-artifacts",
        action="store_true",
        help="fail instead of skipping when the artifact tree is absent (use when publishing)",
    )
    args = parser.parse_args(argv)

    if not args.check:
        parser.print_help()
        return 0

    artifacts = resolve_artifacts(args.artifacts)
    if not artifacts.is_dir():
        return announce_skip(artifacts, require=args.require_artifacts)
    return verify(artifacts)


if __name__ == "__main__":
    sys.exit(main())
