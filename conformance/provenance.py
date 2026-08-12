"""Artifact provenance for the conformance corpus.

Why this exists
---------------
The first pass cited GitHub links pinned to `main`. Those drift, and
api.github.com was unreachable so commit SHAs could not be resolved. A branch
link is not evidence.

This module pins evidence to the **shipped artifact** instead: a package name
and exact version from the public registry, a path inside that distribution,
and a SHA-256 of the file. That is a stronger claim than a git SHA — it is the
bytes a user actually installs — and anyone can reproduce it:

    pip download --no-deps ragas==0.4.3
    unzip -p ragas-0.4.3-py3-none-any.whl <path> | sha256sum

`verify_quotes.py` re-runs the whole check. Run it before publishing anything.

Registry facts recorded 10 August 2026.
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class Artifact:
    """One file inside one published distribution."""
    config_ids: tuple            # corpus records this file is evidence for
    package: str                 # e.g. "ragas==0.4.3"
    registry: str                # "pypi" | "npm"
    path: str                    # path inside the extracted distribution
    sha256: str
    # Verbatim strings that MUST appear in the file. These are the sentences
    # the corpus verdicts quote. If a fragment stops matching, the vendor
    # changed the template and the record is stale.
    fragments: tuple
    note: str = ""


ARTIFACTS: list[Artifact] = []


def add(**kw) -> None:
    ARTIFACTS.append(Artifact(**kw))


# Populated by _build_provenance.py, which hashes the real downloads.
# Kept as generated data rather than hand-typed hashes.
try:
    from conformance._provenance_data import ARTIFACT_DATA
    for _d in ARTIFACT_DATA:
        add(**{**_d, "config_ids": tuple(_d["config_ids"]),
               "fragments": tuple(_d["fragments"])})
except ImportError:  # not yet generated
    ARTIFACT_DATA = []

ARTIFACTS_BY_CONFIG: dict[str, Artifact] = {}
for _a in ARTIFACTS:
    for _c in _a.config_ids:
        ARTIFACTS_BY_CONFIG[_c] = _a
