"""Artifact pinning by package digest.

TODO(port): pinning of every scored artifact to a package digest, ported from
the lab harness.

Why this exists rather than recording a version string: "langchain 0.2.1" is not
a thing a reader can check. The package that was on disk when the score was
produced is. A record pins the digest of the artifact it was derived from, so a
third party can obtain the same bytes and reach the same conclusion -- or show
that they cannot, which is equally useful.

A finding that cannot be traced to pinned bytes is an assertion, not evidence,
and the standard this repository publishes has no business making assertions.
"""

from __future__ import annotations
