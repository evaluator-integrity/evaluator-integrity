"""Framework v0.1 criteria, in executable form.

Every criterion is externally cited, and a test enforces it. A short cited list
is stronger than a long invented one: a criterion we made up is an opinion, and
this project has no standing to publish opinions as criteria. If you want to add a
criterion, find the published result that justifies it first. If there isn't
one, it belongs in a "candidate criteria" file, not here.

`criteria/v0.1/index.md` is the human-readable published version of this file.
They are two renderings of one definition and a test asserts they agree; the
markdown is what people cite, this module is what scores.

TWO CONSTRAINTS, both from criteria/README.md:

  * The ids ARE the published anchors (#C1 ... #C4). They are part of the
    citation surface and never change meaning across versions.
  * A published version is frozen. Adding v0.2 must not change how v0.1 scores.
    When that day comes, this module grows a version dimension -- versions sit
    side by side, never mutate in place. VERSION below is the version this
    module currently scores against, not a value to bump casually.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Criterion:
    id: str
    title: str
    question: str
    why: str
    citation: str
    evidence_required: str
    # What a config must show to pass. Deliberately narrow: a criterion you
    # cannot fail cleanly is not a criterion.
    pass_condition: str
    # Task classes this criterion is evidenced for. Every published result
    # behind C1 and C2 uses tasks with a determinable answer -- GSM8K,
    # competition maths, code, factual QA. None covers summarisation quality,
    # helpfulness or style. Scoring a subjective-task config against them
    # would be extending the evidence past where it goes.
    scope: str = "verifiable"


CRITERIA: list[Criterion] = [
    Criterion(
        id="C1_de_anchoring",
        title="Judge independence (de-anchoring)",
        question=(
            "Does the judge commit to its own answer before it is shown the "
            "candidate output?"
        ),
        why=(
            "Anchoring on the candidate is the mechanism that turns a judge "
            "into a plausibility scorer. Independence is the only intervention "
            "shown to close the basin: committing first drops the "
            "false-positive rate on wrong answers to 0.012, and lifts "
            "discrimination from near chance to 0.96 with no reference answer. "
            "Ensembling fails (a strict three-family ensemble still passes 55% "
            "of hacked wrong answers, its discrimination collapsing from 0.31 "
            "to 0.09); stricter rubrics and stronger judges fail.\n\n"
            "The distinction that matters for scoring: a RECOMPUTE PROMPT also "
            "fails, leaving the false-positive rate at 0.719. Telling a judge "
            "to solve the problem itself, in a prompt that already contains "
            "the candidate, does not de-anchor it. In the paper's words, 'the "
            "decisive variable is not whether the judge sees the candidate but "
            "whether it commits an answer of its own first.'\n\n"
            "THE RESULT IS NOT UNIFORM ACROSS TASK CLASSES, and the two "
            "measurements must be quoted separately. On mathematics (§5.2), "
            "commit-first collapses the false-positive rate on wrong answers "
            "from 0.719 to 0.012 and the single-sample gap falls to zero. On "
            "code (§5.3, best-of-N selection), the same rule reduces the 8B "
            "judge's gap@16 from 0.378 to 0.227 -- a reduction, not an "
            "elimination. Anyone adopting this on code should expect the "
            "smaller effect.\n\n"
            "The fix is also capability-dependent: it 'hurts the 1.7B judge, "
            "whose own committed solutions are mostly wrong' (0.588 -> 0.637) "
            "and helps every larger judge, plateauing by 8B. Below some "
            "unquantified threshold a judge can satisfy this criterion and "
            "measure worse than it would have without it. See "
            "criteria/candidates.md."
        ),
        citation=(
            "Zhou 2026, arXiv:2607.05904v1, §5.1 (the problem and the failed "
            "defences), §5.2 (the de-anchoring fix, mathematics), §5.3 "
            "(best-of-N selection in code and maths), Appendix A (protocol "
            "definitions)"
        ),
        evidence_required=(
            "The judge prompt template and the call sequence. A config passes "
            "only if some stage emits a parseable answer of the judge's own "
            "before any comparison, and acceptance is decided by matching "
            "against it. An in-prompt instruction to 'solve it yourself first' "
            "that produces no such parseable answer is the failed variant -- "
            "record it with recompute_variant=true and score fail.\n\n"
            "AND THE JUDGE'S OWN SOLVE ACCURACY on the task distribution it is "
            "judging. Disclosure, not a threshold: commit-first is "
            "capability-dependent and can make a weak judge worse, but no "
            "citable result fixes the floor. The source states its independence "
            "bound in these terms -- a genuinely independent solver's ceiling "
            "is 1 - solve-acc, 0.07 for a judge solving at 0.93 -- so a reader "
            "given the solve accuracy can apply that bound and decide whether "
            "conformance helps this judge. A number the reader can act on beats "
            "a threshold we cannot source."
        ),
        pass_condition=(
            "The judge emits a parseable answer of its own to the task before "
            "any comparison with the candidate, and acceptance is decided by "
            "matching the candidate against that committed answer rather than "
            "by the judge's holistic score. Candidate visibility at commitment "
            "time is not the discriminator: the source measures the "
            "commit-first protocol with the candidate in full view. "
            "Withholding the candidate entirely (blind solve) is the limiting "
            "case of the same independence, not a separate requirement. An "
            "instruction to solve the problem first that yields no separately "
            "parseable committed answer, and leaves the verdict a holistic "
            "score, is the recompute variant -- record recompute_variant=true "
            "and score fail.\n\n"
            "The match relation is well defined for tasks with a determinable "
            "answer and undefined for code generation, where behavioural "
            "equivalence has no cited definition. A code configuration that "
            "commits an answer but whose match relation is unspecified is "
            "scored insufficient_evidence, not fail. See "
            "criteria/candidates.md."
        ),
    ),
    Criterion(
        id="C2_ground_truth_channel",
        title="Independent ground-truth channel",
        question=(
            "Is there any correctness signal independent of the judge?"
        ),
        why=(
            "If the judge is the only instrument, there is nothing that can "
            "observe the divergence between reported and true quality. The "
            "hidden-anchor method exists precisely because the judge's own "
            "score cannot detect its own failure.\n\n"
            "Reference-free judging is independently measured to be too "
            "generous: judges accept incorrect answers at rates up to 60% with "
            "no reference available, decision flip rates from no-reference to "
            "reference-visible run 9-85%, and judge-human agreement rises from "
            "0.34-0.74 to 0.85-0.96 once reference information is supplied. "
            "Almost all flips are the judge withdrawing credit it had granted."
        ),
        citation=(
            "Zhou 2026, arXiv:2607.05904 (hidden-anchor audit design); "
            "Kranti & Vajjala 2026, arXiv:2607.12885 (reference-free "
            "over-crediting)"
        ),
        evidence_required=(
            "The correctness signal -- exact-match against a trusted source, a "
            "test suite not visible to the generator, human adjudication on a "
            "sample -- and the path showing whether the judge is the only "
            "instrument producing the verdict.\n\n"
            "AND EVIDENCE THAT THE SIGNAL WORKS. A channel that passes "
            "everything satisfies this criterion in letter while carrying no "
            "information, and reports exactly what a working channel reports on "
            "a genuinely correct system. The two are indistinguishable from the "
            "numbers alone, so the distinction has to be evidenced rather than "
            "assumed:\n"
            "  * negative controls -- deliberately incorrect implementations, "
            "each demonstrated to fail the check, covering at least answers "
            "precomputed for the visible cases, suppressed error conditions, "
            "and correct-in-the-typical-case failures at the stated domain "
            "boundaries;\n"
            "  * a positive control -- a known-correct implementation passing "
            "the check in full, establishing that it discriminates rather than "
            "merely rejects.\n\n"
            "A channel offered without this evidence is scored "
            "insufficient_evidence, not pass. This is a requirement on what "
            "must be shown, not a threshold: there is no citable pass line for "
            "how many controls suffice, and inventing one would repeat the "
            "defect corrected in C3."
        ),
        pass_condition=(
            "A correctness signal exists and is independent of the judge.\n\n"
            "This deliberately does NOT require the signal to be held out from "
            "whatever produces or selects outputs. An earlier version did. The "
            "Goodhart argument for that requirement is intuitive but uncited, "
            "and the paper cited here reports the opposite for its own "
            "de-anchored channel -- used as the training reward it stayed "
            "inflation-proof across self-play. Two iterations at n=128 cannot "
            "carry a scoring clause in either direction, so feedback status is "
            "recorded per configuration and reported as a distribution, and no "
            "verdict depends on it. See criteria/candidates.md."
        ),
    ),
    Criterion(
        id="C3_retrieval_controls",
        title="Retrieval and contamination controls",
        question=(
            "Can a passing result have been retrieved rather than derived?"
        ),
        why=(
            "Scores conflate capability with lookup when the environment "
            "permits retrieval. Restricting git history and network access "
            "moved measured resolution rates by 14-21 points on SWE-bench Pro."
        ),
        citation=(
            "Cursor, 'Reward hacking is swamping model intelligence gains', "
            "25 June 2026; SpecBench, arXiv:2605.21384 (visible vs held-out "
            "suites in long-horizon coding agents)"
        ),
        evidence_required=(
            "Environment specification for the eval run: network access, "
            "repository history visibility, and whether task provenance is "
            "reachable from inside the sandbox."
        ),
        pass_condition=(
            "The eval environment restricts the retrieval paths that would let "
            "a candidate look up the answer. Documentation of those paths was "
            "an earlier conjunct and has been removed: the cited source "
            "measures the effect of removing leakage channels and says nothing "
            "about disclosing them, so requiring disclosure was our addition, "
            "not a finding."
        ),
        scope="any",
    ),
    Criterion(
        id="C4_degenerate_pass_resistance",
        title="Resistance to degenerate passes",
        question=(
            "Would a solution that special-cases the visible checks be caught?"
        ),
        why=(
            "Automated red-teaming produced working exploits on 10 of 10 "
            "audited benchmarks and catalogued 219 distinct flaws across eight "
            "recurring classes. Degenerate passing is the most portable of "
            "them, and applies to production configs, not only benchmarks.\n\n"
            "The gap grows with task size: measured pass rates on visible "
            "versus held-out suites diverge by a further 28 percentage points "
            "for every tenfold increase in code size. Small single-function "
            "tasks are therefore the WEAKEST regime in which to demonstrate "
            "this -- a demo built on them understates the effect, which is the "
            "safe direction to be wrong in but worth stating."
        ),
        citation=(
            "BenchJack, arXiv:2605.12673 / Berkeley RDI, 'How We Broke Top AI "
            "Agent Benchmarks', April 2026 (same work; flaw taxonomy V1-V8); "
            "SpecBench, arXiv:2605.21384"
        ),
        evidence_required=(
            "The check suite itself. Does it use randomised or property-based "
            "inputs, or only a fixed, enumerable set the candidate can see?\n\n"
            "AND REACHABILITY, PER HELD-OUT CHECK. A held-out check is "
            "reachable if some known-incorrect implementation fails it while "
            "passing the entire check set visible to the candidate. An "
            "unreachable check cannot catch anything the visible checks would "
            "not have caught first, so it adds no resistance to degenerate "
            "passing however carefully it was written. Reachability is a "
            "property of the two suites as a pair, and is shown by exhibiting "
            "the implementation rather than argued from inspection.\n\n"
            "Counting held-out checks measures nothing; counting reachable "
            "ones measures the resolution of the instrument. A suite offered "
            "without per-check reachability is scored insufficient_evidence, "
            "not pass."
        ),
        pass_condition=(
            "At least part of the correctness check uses inputs the candidate "
            "cannot enumerate in advance."
        ),
        scope="any",
    ),
]

CRITERIA_BY_ID = {c.id: c for c in CRITERIA}
VERSION = "0.1"

VERDICTS = ("pass", "fail", "not_applicable", "insufficient_evidence")

# A configuration's task class decides which criteria apply to it at all.
TASK_CLASSES = ("verifiable", "subjective", "mixed")

SCOPE_NOTE = """
v0.1 applies to evaluators of tasks with a determinable answer.

Every published result behind these criteria uses verifiable tasks: GSM8K and
competition maths, code, and factual QA. None of them covers summarisation
quality, helpfulness, tone or style. For a subjective task it is not even
clear what C1 would mean -- "commit your own answer first" has no obvious
referent when there is no answer.

So configurations whose task class is `subjective` are scored
`not_applicable` on C1 and C2 and reported as a separate population. We are
not claiming those evaluators are sound. We are declining to score them
against evidence that does not reach them, which is the distinction between
a standard and a marketing claim.

Criteria for non-verifiable evaluation are the most obvious gap in v0.1 and
the most useful thing a collaborator could bring.
"""


def applies(criterion_id: str, task_class: str) -> bool:
    """Whether a criterion is in scope for a configuration's task class."""
    c = CRITERIA_BY_ID[criterion_id]
    if c.scope == "any":
        return True
    if task_class == "subjective":
        return False
    return True
