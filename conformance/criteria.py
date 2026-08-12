"""The criteria as executable data.

TODO(port): the four criteria (C1-C4) as structured records -- stable id, title,
what evidence satisfies them, and how each is scored -- ported from the lab
harness so that `criteria/v0.1/index.md` and this module are two renderings of
one definition.

Two constraints on whatever lands here:

  * The ids are the published anchors (#C1 ... #C4). They are part of the
    citation surface and never change meaning across versions.
  * A version that has been published is frozen. Adding v0.2 must not alter
    how v0.1 scores; keep versions side by side rather than mutating one.
"""

from __future__ import annotations
