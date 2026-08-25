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
  * `ours`        -- a quantity the criteria state that is our own arithmetic
                     or construction, not a claim about what a source says. It
                     has no quote and no locator because there is nothing to
                     quote. The criterion text must SAY it is ours -- the check
                     looks for that wording in the text, not in this file --
                     and it passes --require-sources for the same reason it has
                     no source: it is not asserting one. A figure that cannot
                     be labelled this way in the text does not get the status.

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

STATUSES = ("verified", "unsupported", "unverified", "ours")

# Text a criterion must carry for a figure to be recorded as `ours`. The status
# is only honest if the READER can see it, so it is checked against the
# criterion text rather than taken on the ledger's word.
OURS_MARKERS = ("our illustration", "not the source's")


@dataclass(frozen=True)
class Source:
    """One external result the criteria rest on.

    `identifier` must pin a version. "arXiv:2607.05904" names a paper whose v2
    may say something else; "arXiv:2607.05904v1" names bytes. This is the same
    argument provenance.py makes for package digests over version strings.

    `url` and `sha256` record the rendering the quotes were actually read out
    of, so someone else can fetch the same thing and check. Note what the
    digest does and does not pin: it is the HTML *rendering* retrieved on
    `retrieved`, not the canonical PDF, and a site can re-render without the
    paper changing. A digest that stops matching is a prompt to re-read, not
    by itself a finding -- unlike provenance.py's package digests, where
    different bytes mean the vendor shipped something else.
    """
    id: str
    cite: str            # how the criteria cite it, near enough to recognise
    identifier: str      # pinned: arXiv id with version, or a dated document
    url: str = ""        # what was fetched
    retrieved: str = ""  # ISO date the quotes were read out of it
    sha256: str = ""     # digest of that retrieved rendering
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
        url="https://arxiv.org/html/2607.05904v1",
        retrieved="2026-08-25",
        sha256="dd24f41a93c20750e3702b609b67e5b8589e83f1ac304c38e2a5024af22ab7ff",
        note="The hidden-anchor audit design, the de-anchoring fix, and the "
             "best-of-N selection results. C1 rests on it almost entirely; C2 "
             "cites it for the audit design.",
    ),
    Source(
        id="kranti-vajjala2026",
        cite="Kranti & Vajjala 2026",
        identifier="arXiv:2607.12885v1",
        url="https://arxiv.org/html/2607.12885v1",
        retrieved="2026-08-25",
        sha256="ea3a84b4d1a2b4e5de20b9217334985fe46612b5fb477d40256e2895bac5306b",
        note="Reference-free over-crediting. C2's second citation.",
    ),
    Source(
        id="cursor2026",
        cite="Cursor, 'Reward hacking is swamping model intelligence gains'",
        identifier="cursor.com blog, 25 June 2026",
        url="https://cursor.com/blog/reward-hacking-coding-benchmarks",
        retrieved="2026-08-25",
        sha256="d0c2007e9f5aaca57ae5b03017d842277771e3e7f1fe5264605d532265ad050b",
        note="A dated blog post, not a preprint. It is pinned by date and "
             "title and nothing else, which is weaker than an arXiv version "
             "and is the reason C3's figure is the one most worth re-reading "
             "before publication.",
    ),
    Source(
        id="benchjack",
        cite="BenchJack / Berkeley RDI, 'How We Broke Top AI Agent Benchmarks'",
        identifier="arXiv:2605.12673v1",
        url="https://arxiv.org/html/2605.12673v1",
        retrieved="2026-08-25",
        sha256="309dec927970429b1dfd47b1b7a9533eab9166abdbaf260a8c7cd67c5b5ce32a",
        note="Same work under two names. The flaw taxonomy V1-V8 is Figure 6a.",
    ),
    Source(
        id="specbench",
        cite="SpecBench",
        identifier="arXiv:2605.21384v1",
        url="https://arxiv.org/html/2605.21384v1",
        retrieved="2026-08-25",
        sha256="d535c7420287b344afb066f7267cbe4c28c5fe510ffadea94c0d436226946ca5",
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
        locator="abstract", status="verified",
        supports=("committing first, with the candidate still in view, drops "
                  "the false-positive rate on wrong answers to 0.012",),
        numbers=("0.012",),
        quote="committing first--candidate still in view--drops it to 0.012",
    ),
    Claim(
        criterion_id="C1_de_anchoring", field="why", source="zhou2026",
        locator="abstract", status="verified",
        supports=("blind solving, the limiting case of the same "
                  "independence, lifts discrimination from near chance to "
                  "0.96 with no reference answer",),
        numbers=("0.96",),
        quote="blind solving lifts discrimination from near chance to 0.96 "
              "with no reference answer",
        note="Was unsupported until 25 Aug 2026: the criterion read 0.96 as an "
             "effect of committing first, which the source attributes to blind "
             "solving in the same sentence. Now attributed as the source does. "
             "The published markdown already had this right, and the module did "
             "not -- two renderings of one definition disagreeing about which "
             "arm a headline number belongs to, which is the conflation the "
             "21 Aug pass condition fix removed from the other half of C1.",
    ),
    Claim(
        criterion_id="C1_de_anchoring", field="why", source="zhou2026",
        locator="§1 Introduction", status="verified",
        supports=("a strict three-family ensemble still passes 55% "
                  "of hacked wrong answers, its discrimination collapsing from "
                  "0.31 to 0.09",),
        numbers=("55%", "0.31", "0.09"),
        quote="a three-family ensemble that accepts only when all judges "
              "agree still passes 55% of the hacked wrong answers, its "
              "discrimination collapsing from 0.31 to 0.09",
        note="The criterion's 'strict' renders the source's 'accepts only "
             "when all judges agree'. The abstract states the same result in "
             "different words ('a strict three-family ensemble still accepts "
             "55%'); this is the introduction's fuller form.",
    ),
    Claim(
        criterion_id="C1_de_anchoring", field="why", source="zhou2026",
        locator="abstract", status="verified",
        supports=("leaving the false-positive rate at 0.719",),
        numbers=("0.719",),
        quote="the recompute prompt leaves the false-positive rate on wrong "
              "answers at 0.719",
        note="The figure that decides how a whole class of configurations "
             "scores -- a recompute prompt is the most common near-miss in "
             "the corpus.",
    ),
    Claim(
        criterion_id="C1_de_anchoring", field="why", source="zhou2026",
        locator="abstract", status="verified",
        supports=("'the "
                  "decisive variable is not whether the judge sees the "
                  "candidate but whether it commits an answer of its own "
                  "first.'",),
        quote="The decisive variable is not whether the judge sees the "
              "candidate but whether it commits an answer of its own first",
        note="The criterion closes the quotation with a full stop; the source "
             "sentence continues after a colon. The words are the source's, "
             "the terminal punctuation is ours, and the quote here is the "
             "source's form.",
    ),
    Claim(
        criterion_id="C1_de_anchoring", field="why", source="zhou2026",
        locator="§5.3", status="verified",
        supports=("the same rule reduces the 8B "
                  "judge's gap@16 from 0.378 to 0.227",),
        numbers=("8B", "16", "0.378", "0.227"),
        quote="Applying the commit-first rule to the same pool, the 8B "
              "judge's gap@16 falls from 0.378 to 0.227 (paired reduction CI "
              "[0.064,0.237]) and its single-sample gap falls to zero",
        note="The source pairs the reduction with a confidence interval the "
             "criterion does not carry. Omitting it understates nothing, but "
             "a reader quoting the criterion gets a point estimate where the "
             "source gave an interval.",
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
        locator="§5.3", status="verified",
        supports=("(0.588 -> 0.637)",),
        numbers=("0.588", "0.637"),
        quote="committing hurts the 1.7B judge, whose own committed solutions "
              "are mostly wrong (0.588->0.637)",
    ),
    Claim(
        criterion_id="C1_de_anchoring", field="why", source="zhou2026",
        locator="§5.3", status="verified",
        supports=("helps every larger judge, plateauing by 8B",),
        quote="helps every larger judge, plateauing by 8B",
    ),
    Claim(
        criterion_id="C1_de_anchoring", field="evidence_required",
        source="zhou2026", locator="§4", status="verified",
        supports=("a genuinely independent solver's ceiling "
                  "is 1 - solve-acc",),
        numbers=("1",),
        quote="A verdict either commits an answer independently of the "
              "candidate--inheriting the judge-side ceiling 1 - solve-acc",
    ),
    Claim(
        criterion_id="C1_de_anchoring", field="evidence_required",
        source="zhou2026", locator="§4", status="verified",
        supports=("reports a 0.07 ceiling for the setting it "
                  "audits",),
        numbers=("0.07",),
        quote="its FPR=0.719 against the 0.07 ceiling",
    ),
    Claim(
        criterion_id="C1_de_anchoring", field="evidence_required",
        source="zhou2026", locator="", status="ours",
        supports=("Our illustration, not the source's: 0.07 is the ceiling a "
                  "judge solving at 0.93 would carry",),
        numbers=("0.93",),
        note="Was unsupported until 25 Aug 2026, when it read as the source's "
             "own formulation. It is 1 - 0.07, worked backwards by us. The "
             "arithmetic was never wrong; presenting it as the source's was. "
             "It stays because this is the one figure C1 hands the reader to "
             "compute with, and a worked example makes the bound usable -- but "
             "the text now says whose example it is.",
    ),

    # ---- C2 -------------------------------------------------------------
    Claim(
        criterion_id="C2_ground_truth_channel", field="why",
        source="kranti-vajjala2026", locator="§5.1", status="verified",
        supports=("of incorrect answers reaches 60% for the worst "
                  "judge and dataset pair measured",),
        numbers=("60%",),
        quote="for Telugu, we observe C2 scores as high as 60% for one judge "
              "model (Gemma3-27B on MATA in Figure 4(b) )",
        note="Corrected 21 Aug 2026 from 'judges accept incorrect answers at "
             "rates up to 60%', which presented one judge's worst cell on one "
             "Telugu dataset as a general rate. Quote re-read from the source "
             "25 Aug: the recorded form said 'Figure 4b' where the source "
             "writes 'Figure 4(b)'. NB the quote's 'C2' is the paper's own "
             "metric (acceptance of incorrect answers), not our criterion C2.",
    ),
    Claim(
        criterion_id="C2_ground_truth_channel", field="why",
        source="kranti-vajjala2026", locator="abstract", status="verified",
        supports=("flips the judge's decisions by as much as 85% in some "
                  "settings and not at all in others",),
        numbers=("85%",),
        quote="adding reference answer information to the prompt flips the "
              "judge model's correct/incorrect decisions by as much as 85% in "
              "some experimental settings",
        note="Was unsupported until 25 Aug 2026 as '9-85%'. 85% is the "
             "source's maximum, not the top of a measured range, and no 9% "
             "floor exists -- the paper's flip-rate table contains a delta of "
             "0.00 (Sarvam-105B on Arabic), which the invented floor "
             "contradicted. Stated now as a maximum with the null case beside "
             "it, which is what the source supports and is also the weaker "
             "claim.",
    ),
    Claim(
        criterion_id="C2_ground_truth_channel", field="why",
        source="kranti-vajjala2026", locator="Table 2", status="verified",
        supports=("judge-human agreement rises from "
                  "0.34-0.74 to 0.85-0.96 once reference information is "
                  "supplied",),
        numbers=("0.34", "0.74", "0.85", "0.96"),
        quote="JM NR RV RC H1 H2 H1 H2 H1 H2 G3.1FL 0.74 0.74 0.96 0.96 0.96 "
              "0.96 G3 0.34 0.33 0.85 0.85 0.86 0.86 Q3 0.42 0.42 0.90 0.90 "
              "0.89 0.89",
        note="Read off Table 2 (Judge Responses Alignment with Human "
             "Annotations) rather than quoted from a sentence: the no-"
             "reference column spans 0.34-0.74 and the reference-visible "
             "column 0.85-0.96 across the three judges, against annotator H1. "
             "Recording the row is what makes the range re-checkable; a "
             "sentence stating it does not exist in the paper.",
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
        source="zhou2026", locator="Figure 1(a) caption; §5 Setup",
        status="verified",
        supports=("Five self-play iterations on a "
                  "128-item audit subset, three seeds, one task family -- two "
                  "iterations is the paper's default elsewhere",),
        numbers=("128",),
        quote="Five self-play iterations: the judge's pass rate climbs to "
              "~0.9 and holds while anchor-verified accuracy stays "
              "statistically flat (n=128 audit per iteration, three seeds; "
              "thin lines seeds, bold mean)",
        note="Was unsupported until 25 Aug 2026 as 'two iterations at n=128', "
             "which conflated the paper's default ('we run two iterations and "
             "three seeds unless noted') with the n=128 audit, where Figure "
             "1(a) reports five. The reasoning it carries is unchanged and "
             "does not depend on which: an experiment this size cannot carry "
             "a scoring clause in either direction. A reason for caution that "
             "misstates the evidence is still misstated, which is why it was "
             "corrected rather than left as close enough.",
    ),

    # ---- C3 -------------------------------------------------------------
    Claim(
        criterion_id="C3_retrieval_controls", field="why", source="cursor2026",
        locator="body", status="verified",
        supports=("moved measured resolution rates by up to 20.7 points",
                  "14.1 and 20.7 points on "
                  "two models, under 1 point on a third in the same experiment",),
        numbers=("20.7", "14.1", "1"),
        quote="On SWE-bench Pro, it was under 1 point for Opus 4.6, 14.1 "
              "points for Opus 4.8 Max and 20.7 points for Composer 2.5.",
        note="Corrected 21 Aug 2026: previously '14-21 points', a range that "
             "presented a model-dependent effect as a property of the "
             "restriction; the same experiment measured under 1 point on a "
             "third model, now stated. Sole non-preprint source here; a blog "
             "post can be edited in place, so most likely to become "
             "unverifiable.",
    ),

    # ---- C4 -------------------------------------------------------------
    Claim(
        criterion_id="C4_degenerate_pass_resistance", field="why",
        source="benchjack", locator="§1 Introduction, contributions list",
        status="verified",
        supports=("catalogued "
                  "219 distinct flaws across eight recurring classes and produced "
                  "10 working exploits",),
        numbers=("10", "219"),
        quote="We utilized BenchJack to audit 10 popular agent benchmarks, "
              "yielding 219 flaws in 8 recurring classes and 10 working "
              "exploits.",
        note="Corrected 21 Aug 2026 from 'working exploits on 10 of 10 "
             "audited benchmarks', which the source contradicts: 10 exploits "
             "ACROSS 10 benchmarks, near-perfect scores on 'most', and "
             "Figure 5's caption says nine. Re-read 25 Aug: the recorded form "
             "wrote 'BENCHJACK' where the source writes 'BenchJack', and gave "
             "the locator as the abstract -- the sentence is in the "
             "introduction's contributions list. The abstract states the same "
             "flaw count differently ('surfacing 219 distinct flaws across "
             "the eight classes').",
    ),
    Claim(
        criterion_id="C4_degenerate_pass_resistance", field="why",
        source="benchjack", locator="Figure 5 caption", status="verified",
        supports=("nine benchmarks hacked on almost all instances",),
        numbers=(),
        quote="nine benchmarks are hacked on almost all of instances",
        note="The caption's own count, carried in the prose rather than "
             "flattened into '10 of 10'.",
    ),
    Claim(
        criterion_id="C4_degenerate_pass_resistance", field="why",
        source="benchjack", locator="abstract", status="verified",
        supports=("catalogued 219 distinct flaws",),
        numbers=("219",),
        quote="surfacing 219 distinct flaws across the eight classes",
    ),
    Claim(
        criterion_id="C4_degenerate_pass_resistance", field="why",
        source="benchjack", locator="Figure 2 caption; §4.1",
        status="verified",
        supports=("across eight "
                  "recurring classes",),
        quote="The eight recurring flaw classes (V1-V8) in our flaw taxonomy, "
              "covering issues such as trust boundary violation (V7), "
              "isolation failure (V1), and remote code execution (V3).",
        note="The quote this row carried until 25 Aug 2026 -- a comma-joined "
             "list of Figure 6a's abbreviated labels -- is not in the paper. I "
             "had taken it from criteria/candidates.md's rendering and marked "
             "the row verified on that. Replaced with Figure 2's caption, "
             "which states the count and the taxonomy in the paper's own "
             "words. A word-quantity, so the numeral sweep does not reach it "
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
        source="cursor2026", locator="body, 'How agents get the answer'",
        status="verified",
        supports=("63% of successful resolutions retrieved the fix",),
        numbers=("63%",),
        quote="On SWE-bench Pro, we found that 63% of successful Opus 4.8 Max "
              "resolutions retrieved the fix rather than derived it.",
        note="Attribution confirmed 25 Aug 2026. It had been assigned to "
             "Cursor by adjacency -- it shares a sentence with the SWE-bench "
             "Pro restriction figure -- and the source bears that out. Note "
             "the source names the model; the published markdown says 'on one "
             "model', which is weaker than the source rather than stronger.",
    ),
    Claim(
        criterion_id="C4_degenerate_pass_resistance", field="published_text",
        source="specbench", locator="abstract", status="verified",
        supports=('a 2,900-line "compiler" that memorised test inputs',),
        numbers=("2,900",),
        quote='including a 2,900-line hash-table "compiler" that memorizes '
              'test inputs',
        note="Attribution confirmed 25 Aug 2026; the adjacency guess to "
             "SpecBench was right. The published markdown drops the source's "
             "'hash-table', which loses the detail that makes the example "
             "legible -- the artefact was a lookup table wearing a compiler's "
             "name.",
    ),
    Claim(
        criterion_id="C4_degenerate_pass_resistance", field="why",
        source="specbench", locator="Figure 2 caption", status="verified",
        supports=("grows by approximately 27 percentage "
                  "points for every "
                  "tenfold increase in code size",
                  "90th-percentile gap",
                  "a weak fit, "
                  "R\u00b2 = 0.21",),
        numbers=("27", "0.21", "90"),
        quote="the 90th-percentile gap grows by approximately 27 percentage "
              "points for every tenfold increase in LOC (R\u00b2 = 0.21)",
        note="Corrected 21 Aug 2026: previously read '28 percentage points' "
             "with no qualifiers, taking the abstract's figure over the body "
             "and Figure 2 caption, which both say 27, and dropping that it "
             "is the 90th-percentile (worst-case) gap with a weak fit. The "
             "prose now says 27 with both qualifiers.",
    ),
    Claim(
        criterion_id="C4_degenerate_pass_resistance", field="why",
        source="specbench", locator="abstract", status="verified",
        supports=("rounds it to 28",),
        numbers=("28",),
        quote="it grows by 28 percentage points for every tenfold increase "
              "in code size",
        note="The source's own internal inconsistency, attributed rather "
             "than silently resolved: the abstract says 28 where the body "
             "and Figure 2 say 27.",
    ),
]
