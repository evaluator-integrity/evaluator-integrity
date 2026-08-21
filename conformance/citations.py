"""The citation chain: every claim in the criteria, tied to the source it rests on.

Why this exists
---------------
`test_every_criterion_is_externally_cited` asserts that each criterion's
`citation` field matches `arXiv:\\d` or a four-digit year. That is a regex on
the *shape* of a string. A criterion citing "arXiv:0000.00000" passes it, and so
does a criterion whose citation is real but whose numbers came from somewhere
else entirely. It is the degenerate pass this repository's own C4 describes:
a check nothing can fail without having already failed something visible.

This module is the check that replaces it. `provenance.py` does the same job one
level down -- it ties a corpus verdict to the bytes of a shipped package -- and
this ties a *criterion* to the published result it claims to rest on.

The unit is the claim, not the criterion. A criterion is not one assertion; C1's
rationale states nine separate measurements, and "C1 is cited" says nothing
about whether any particular one of them is. So each quantity the criteria state
is recorded here individually, with the source, the locator inside it, and the
verbatim span it was read from.

What this can and cannot establish
----------------------------------
It cannot establish that a paper says what we say it says. Only reading the
paper does that, and the papers are not in this repository.

What it does establish, on a bare clone with no network:

  * Every number stated in the criteria is DECLARED -- attached to a source and
    a locator, with its status recorded. A number appearing in a criterion with
    no entry here fails the build. This is the property that was missing: a
    figure could be added to a rationale and nothing anywhere asked where it
    came from.
  * Every recorded quote still matches the criterion text it backs. `supports`
    holds exact substrings of the criterion field. Edit the criterion away from
    its evidence and the chain breaks, which is the failure mode that produced
    C3's documentation conjunct and C2's held-out clause.
  * Every number a claim says it accounts for actually appears in that claim's
    quote. A quote that does not contain the figure it is offered for is not
    evidence for it.

Status, and why unverified is a value rather than an absence
------------------------------------------------------------
  * `verified`    -- the span was read back out of the pinned source. `quote`
                     is that span.
  * `unsupported` -- the source was read and does not support the claim.
                     `quote` is what it says instead. This is a finding against
                     our own text, and it stays visible until the text changes.
  * `unverified`  -- stated in the criteria, not yet read back out of the
                     pinned source. No quote, because inventing one is the exact
                     failure this project exists to detect elsewhere.

An empty slot cannot be cited by mistake; an invention can. So an unverified
claim is recorded as unverified and counted, rather than left out of the ledger
where its absence would read as coverage.

DIGITS ONLY. The ledger scans for numerals. "eight recurring classes" and "nine
benchmarks" are quantities written as words and are not caught, so a claim
carrying one is recorded here deliberately rather than by the sweep. Stating
this plainly beats implying the coverage is total.
"""

from __future__ import annotations

import pathlib
import re
from dataclasses import dataclass

from conformance.criteria import CRITERIA_BY_ID

# Fields of a Criterion that may state an externally sourced quantity, plus
# `published_text` -- the criterion's section of criteria/vX.Y/index.md.
#
# The markdown is not a copy of the module. It is the rendering people cite,
# and it says things the module does not: C3's "on one model, 63% of successful
# resolutions retrieved the fix" and C4's 2,900-line compiler are stated only
# there. A chain that stopped at the module would leave the citation surface
# itself unchecked, which is the wrong half to cover.
CITED_FIELDS = ("question", "why", "evidence_required", "pass_condition",
                "published_text")

STATUSES = ("verified", "unsupported", "unverified")


@dataclass(frozen=True)
class Source:
    """One external result the criteria rest on.

    `identifier` must pin a version. "arXiv:2607.05904" names a paper whose v2
    may say something else; "arXiv:2607.05904v1" names bytes. This is the same
    argument provenance.py makes for package digests over version strings.
    """
    id: str
    cite: str            # how the criteria cite it, near enough to recognise
    identifier: str      # pinned: arXiv id with version, or a dated document
    note: str = ""


@dataclass(frozen=True)
class Claim:
    """One assertion a criterion makes, and the span of source behind it."""
    criterion_id: str
    field: str           # which CITED_FIELDS entry states it
    source: str          # Source.id
    locator: str         # "§5.2", "abstract", "Figure 5 caption"
    status: str
    # Exact substrings of the criterion field this claim backs. These are the
    # link: if the criterion text is edited and these stop matching, the chain
    # is broken and the build says so.
    supports: tuple
    # Numerals this claim accounts for, as they appear in the criterion text.
    # The ledger requires every numeral in the criteria to be claimed by
    # exactly one entry here.
    numbers: tuple = ()
    quote: str = ""      # verbatim span; empty iff status == "unverified"
    note: str = ""


SOURCES: list[Source] = [
    Source(
        id="zhou2026",
        cite="Zhou 2026",
        identifier="arXiv:2607.05904v1",
        note="The hidden-anchor audit design, the de-anchoring fix, and the "
             "best-of-N selection results. C1 rests on it almost entirely; C2 "
             "cites it for the audit design.",
    ),
    Source(
        id="kranti-vajjala2026",
        cite="Kranti & Vajjala 2026",
        identifier="arXiv:2607.12885v1",
        note="Reference-free over-crediting. C2's second citation.",
    ),
    Source(
        id="cursor2026",
        cite="Cursor, 'Reward hacking is swamping model intelligence gains'",
        identifier="cursor.com blog, 25 June 2026",
        note="A dated blog post, not a preprint. It is pinned by date and "
             "title and nothing else, which is weaker than an arXiv version "
             "and is the reason C3's figure is the one most worth re-reading "
             "before publication.",
    ),
    Source(
        id="benchjack",
        cite="BenchJack / Berkeley RDI, 'How We Broke Top AI Agent Benchmarks'",
        identifier="arXiv:2605.12673v1",
        note="Same work under two names. The flaw taxonomy V1-V8 is Figure 6a.",
    ),
    Source(
        id="specbench",
        cite="SpecBench",
        identifier="arXiv:2605.21384v1",
        note="Visible versus held-out suites in long-horizon coding agents. "
             "Cited by both C3 and C4.",
    ),
]

SOURCES_BY_ID = {s.id: s for s in SOURCES}


# Tokens that look numeric but address a document rather than measure anything:
# section numbers, arXiv ids, criterion and taxonomy ids, criteria versions.
# Stripped before the sweep so the ledger is not asked to source "§5.2".
_MONTHS = ("January|February|March|April|May|June|July|August|September|"
           "October|November|December")
_ADDRESSES = (
    r"§\d+(?:\.\d+)?",
    r"arXiv:\d+\.\d+(?:v\d+)?",
    rf"\b\d{{1,2}} (?:{_MONTHS}) \d{{4}}\b",   # before the bare-year rule:
    r"\b(?:19|20)\d\d\b",                      # "14 July 2026" hides a 14
    r"\bC[1-5]\b",
    r"\bv\d+\.\d+\b",
    r"\bV[1-8]\b",
)

# A quantity as the criteria write it: the numeral plus the unit that makes it
# readable back, so the ledger reads like the prose it is auditing. The
# comma-grouped form comes first, or "2,900" is swept up as a 2 and a 900.
_NUMERAL = re.compile(r"\d{1,3}(?:,\d{3})+|\d+(?:\.\d+)?(?:%|\s?B\b)?")


# The italic source line under each criterion. It is an address, not prose that
# makes claims, and every figure in it is a date or an identifier.
_SOURCE_LINE = re.compile(r"^\*Sources?:.*?\*\s*$", re.M | re.S)


def normalise(n: str) -> str:
    """A numeral stripped to the quantity, for comparing across renderings.

    The module writes "9-85%" where the markdown writes "from 9% to 85%", and
    "1.7B" where a quote writes the same thing. Comparing the rendered forms
    would report a difference in typography as a missing source.
    """
    return n.replace(",", "").rstrip("%").rstrip("B").strip()


def published_sections(version: str | None = None) -> dict:
    """Each criterion's section of the published markdown, keyed by anchor id.

    Only the version this package currently scores against. Frozen versions are
    not re-checked here: their text cannot change, so a chain over them could
    only ever break by the ledger moving, and the ledger belongs to the live
    version.
    """
    from conformance import CRITERIA_VERSION
    version = version or CRITERIA_VERSION
    path = (pathlib.Path(__file__).resolve().parents[1]
            / "criteria" / f"v{version}" / "index.md")
    text = path.read_text()
    out, current, buf = {}, None, []
    for line in text.splitlines():
        # A section ends at the next heading of any kind, not at the next
        # heading that happens to carry a criterion anchor. C4 is the last
        # criterion on the page, and the sections after it -- what v0.1 does
        # not cover, the changelog -- would otherwise be read as part of it.
        # A figure added there would be attributed to C4, and a supports span
        # could resolve against text belonging to a different section.
        if re.match(r"#{1,3} ", line):
            if current:
                out[current] = "\n".join(buf)
            head = re.match(r"#{2,3} .*\{#(C[1-5])\}\s*$", line)
            current, buf = (head.group(1) if head else None), []
            continue
        if current:
            buf.append(line)
    if current:
        out[current] = "\n".join(buf)
    return {k: _SOURCE_LINE.sub(" ", v) for k, v in out.items()}


def criterion_text(criterion, field: str) -> str:
    """The span of criteria text a claim's `field` names."""
    if field == "published_text":
        return published_sections().get(criterion.id.split("_", 1)[0], "")
    return getattr(criterion, field)


def numerals(text: str) -> set:
    """Every measured quantity stated in a span of criteria text.

    Digits only -- see the module docstring. Quantities written as words are
    invisible here and have to be declared by hand.
    """
    for pattern in _ADDRESSES:
        text = re.sub(pattern, " ", text)
    return set(_NUMERAL.findall(text))


# The ledger. One entry per assertion the criteria make.
#
# Read the status column before the quotes. Most of this corpus is `unverified`:
# the criteria state the figure, and nobody has yet read the span back out of
# the pinned source and recorded it here. That is the state this module exists
# to make countable, not a state it invents.
CLAIMS: list[Claim] = [

    # ---- C1 -------------------------------------------------------------
    Claim(
        criterion_id="C1_de_anchoring", field="why", source="zhou2026",
        locator="§5.2", status="unverified",
        supports=("committing first drops the "
                  "false-positive rate on wrong answers to 0.012, and lifts "
                  "discrimination from near chance to 0.96 with no reference "
                  "answer",),
        numbers=("0.012", "0.96"),
    ),
    Claim(
        criterion_id="C1_de_anchoring", field="why", source="zhou2026",
        locator="§5.1", status="unverified",
        supports=("a strict three-family ensemble still passes 55% "
                  "of hacked wrong answers, its discrimination collapsing from "
                  "0.31 to 0.09",),
        numbers=("55%", "0.31", "0.09"),
    ),
    Claim(
        criterion_id="C1_de_anchoring", field="why", source="zhou2026",
        locator="§5.2", status="unverified",
        supports=("leaving the false-positive rate at 0.719",),
        numbers=("0.719",),
        note="The recompute-variant measurement. It is the figure that decides "
             "how a whole class of configurations scores -- a recompute prompt "
             "is the single most common near-miss in the corpus -- and it is "
             "unverified.",
    ),
    Claim(
        criterion_id="C1_de_anchoring", field="why", source="zhou2026",
        locator="§5.2", status="verified",
        supports=("'the "
                  "decisive variable is not whether the judge sees the "
                  "candidate but whether it commits an answer of its own "
                  "first.'",),
        quote="the decisive variable is not whether the judge sees the "
              "candidate but whether it commits an answer of its own first.",
        note="The sentence C1's pass condition is built on: it is why "
             "candidate visibility at commitment time is not the "
             "discriminator.",
    ),
    Claim(
        criterion_id="C1_de_anchoring", field="why", source="zhou2026",
        locator="§5.3", status="unverified",
        supports=("the same rule reduces the 8B "
                  "judge's gap@16 from 0.378 to 0.227",),
        numbers=("8B", "16", "0.378", "0.227"),
    ),
    Claim(
        criterion_id="C1_de_anchoring", field="why", source="zhou2026",
        locator="§5.3", status="verified",
        supports=("'hurts the 1.7B judge, "
                  "whose own committed solutions are mostly wrong'",),
        quote="hurts the 1.7B judge, whose own committed solutions are mostly "
              "wrong",
        numbers=("1.7B",),
    ),
    Claim(
        criterion_id="C1_de_anchoring", field="why", source="zhou2026",
        locator="§5.3", status="unverified",
        supports=("(0.588 -> 0.637)",),
        numbers=("0.588", "0.637"),
    ),
    Claim(
        criterion_id="C1_de_anchoring", field="why", source="zhou2026",
        locator="§5.3", status="verified",
        supports=("helps every larger judge, plateauing by 8B",),
        quote="helps every larger judge, plateauing by 8B",
    ),
    Claim(
        criterion_id="C1_de_anchoring", field="evidence_required",
        source="zhou2026", locator="§5.3", status="unverified",
        supports=("a genuinely independent solver's ceiling "
                  "is 1 - solve-acc, 0.07 for a judge solving at 0.93",),
        numbers=("1", "0.07", "0.93"),
        note="The locator is inferred from C1's own citation line and is not "
             "confirmed. This is the bound the evidence requirement asks a "
             "reader to apply themselves, so it is the one figure here whose "
             "verification a reader most directly depends on.",
    ),

    # ---- C2 -------------------------------------------------------------
    Claim(
        criterion_id="C2_ground_truth_channel", field="why",
        source="kranti-vajjala2026", locator="", status="unverified",
        supports=("judges accept incorrect answers at rates up to 60% with "
                  "no reference available",),
        numbers=("60%",),
    ),
    Claim(
        criterion_id="C2_ground_truth_channel", field="why",
        source="kranti-vajjala2026", locator="", status="unverified",
        supports=("decision flip rates from no-reference to "
                  "reference-visible run 9-85%",),
        numbers=("9", "85%"),
    ),
    Claim(
        criterion_id="C2_ground_truth_channel", field="why",
        source="kranti-vajjala2026", locator="", status="unverified",
        supports=("judge-human agreement rises from "
                  "0.34-0.74 to 0.85-0.96 once reference information is "
                  "supplied",),
        numbers=("0.34", "0.74", "0.85", "0.96"),
    ),
    Claim(
        criterion_id="C2_ground_truth_channel", field="pass_condition",
        source="zhou2026", locator="abstract; §5.2", status="verified",
        supports=("used as the training reward it stayed "
                  "inflation-proof across self-play",),
        quote="Used as the training reward, the de-anchored channel keeps the "
              "false-positive rate at zero across self-play, preventing the "
              "basin rather than only detecting it.",
        note="This is the quote that removed C2's held-out clause. The clause "
             "asserted the opposite of the cited source and no check caught "
             "it, which is the gap this module closes.",
    ),
    Claim(
        criterion_id="C2_ground_truth_channel", field="pass_condition",
        source="zhou2026", locator="§5.2", status="unverified",
        supports=("Two iterations at n=128 cannot "
                  "carry a scoring clause in either direction",),
        numbers=("128",),
        note="Our own characterisation of the experiment's size. It is load "
             "bearing in the other direction -- it is the reason the held-out "
             "requirement was removed rather than inverted -- so it wants "
             "verifying as much as a figure we assert positively.",
    ),

    # ---- C3 -------------------------------------------------------------
    Claim(
        criterion_id="C3_retrieval_controls", field="why", source="cursor2026",
        locator="", status="unverified",
        supports=("Restricting git history and network access "
                  "moved measured resolution rates by 14-21 points on "
                  "SWE-bench Pro.",),
        numbers=("14", "21"),
        note="C3's only quantity, from the only source here that is not a "
             "versioned preprint. A blog post can be edited in place with no "
             "version to fall back on, so this is the claim most likely to "
             "become unverifiable rather than merely unverified.",
    ),

    # ---- C4 -------------------------------------------------------------
    Claim(
        criterion_id="C4_degenerate_pass_resistance", field="why",
        source="benchjack", locator="Figure 5 caption", status="unsupported",
        supports=("Automated red-teaming produced working exploits on 10 of 10 "
                  "audited benchmarks",),
        numbers=("10",),
        quote="nine benchmarks are hacked on almost all of instances",
        note="RECORDED AS UNSUPPORTED IN criteria/candidates.md AND STILL "
             "STANDING IN C1-C4. The paper reports 10 working exploits across "
             "10 audited benchmarks and describes near-perfect scores on "
             "'most of the benchmarks'; its Figure 5 caption says nine. "
             "'10 of 10' reads as one exploit per benchmark, which is a "
             "stronger claim than either. It still stands in both renderings "
             "-- criteria.py's rationale and criteria/v0.1/index.md -- so a "
             "reader who cites C4 today cites it.",
    ),
    Claim(
        criterion_id="C4_degenerate_pass_resistance", field="why",
        source="benchjack", locator="", status="unverified",
        supports=("catalogued 219 distinct flaws",),
        numbers=("219",),
    ),
    Claim(
        criterion_id="C4_degenerate_pass_resistance", field="why",
        source="benchjack", locator="Figure 6a", status="verified",
        supports=("across eight "
                  "recurring classes",),
        quote="V1 Isolation, V2 Answers in test, V3 RCE, V4 LLM judge, "
              "V5 Weak match, V6 Logic gaps, V7 Trust untrusted, "
              "V8 Excess perms",
        note="The eight labels of Figure 6a, not a contiguous sentence in the "
             "paper. A word-quantity, so the numeral sweep does not reach it "
             "and it is declared here deliberately.",
    ),
    # ---- stated only in the published markdown --------------------------
    # These two are in criteria/v0.1/index.md and in neither the module's
    # rationale nor its evidence requirements. The module is what scores, so
    # nothing in the scorer can be checked against them; they reach the reader
    # anyway, because the markdown is the rendering people cite. That asymmetry
    # is the reason the chain covers published_text at all.
    Claim(
        criterion_id="C3_retrieval_controls", field="published_text",
        source="cursor2026", locator="", status="unverified",
        supports=("63% of successful resolutions retrieved the fix",),
        numbers=("63%",),
        note="Attributed to Cursor because it shares a sentence with the "
             "14-21 point SWE-bench Pro figure, which C3 attributes there. "
             "C3 cites two sources and the markdown does not say which this "
             "came from, so the attribution is inference from adjacency and "
             "wants confirming with the figure itself.",
    ),
    Claim(
        criterion_id="C4_degenerate_pass_resistance", field="published_text",
        source="specbench", locator="", status="unverified",
        supports=('a 2,900-line "compiler" that memorised test inputs',),
        numbers=("2,900",),
        note="Same adjacency argument as C3's 63%: it sits in the sentence "
             "carrying SpecBench's code-size divergence figure. C4 cites both "
             "BenchJack and SpecBench and a memorising compiler would sit as "
             "naturally in either.",
    ),
    Claim(
        criterion_id="C4_degenerate_pass_resistance", field="why",
        source="specbench", locator="", status="unverified",
        supports=("measured pass rates on visible "
                  "versus held-out suites diverge by a further 28 percentage "
                  "points for every tenfold increase in code size",),
        numbers=("28",),
    ),
]
