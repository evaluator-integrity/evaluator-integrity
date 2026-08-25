---
# This front matter block must stay, even though it is nearly empty. Jekyll
# copies files without front matter verbatim, which would serve this page as
# raw markdown instead of rendering it. The layout comes from the `defaults`
# rule in /_config.yml.
title: "Evaluator Integrity Criteria v0.1"
---

# Evaluator Integrity Criteria

**Version 0.1 — provisional. Not yet published.**

**Publication date:** not yet published.
**Status:** draft. This version has no frozen text and must not be cited.

<!--
On publication, replace the three lines above with the real date and a status of
"current". From that moment this file is frozen: corrections create v0.2, they
never edit v0.1. The per-criterion anchor ids are the citation surface and must never
change meaning.
-->


These are the criteria the accompanying conformance study measured against.
They are drawn from published results, not invented here, and they will be
revised. Treat this as a working draft put in public early rather than a
standard — the citation list is doing the load-bearing work, not our authority.

Criticism is the point. If a criterion is wrong, unmeasurable, or missing,
that is the most useful thing you can tell us.

## Scope {#scope}

These criteria apply to **automated evaluators used to make decisions about AI
system quality** — LLM judges, test harnesses, and the configurations that wrap
them. They do not assess model quality. They assess whether the instrument
measuring model quality can be relied on.

**v0.1 covers evaluators of tasks with a determinable answer.** Every published
result behind C1 and C2 uses verifiable tasks: GSM8K and competition
mathematics, code, and factual question answering. None covers summarisation
quality, helpfulness, tone or style. For a subjective task it is not clear what
C1 would even mean — "commit your own answer first" has no obvious referent
when there is no answer to commit to.

Configurations for subjective tasks are therefore scored `not applicable` on C1
and C2 and reported as a separate population. This is not a claim that those
evaluators are sound. It is a refusal to score them against evidence that does
not reach them. **Criteria for non-verifiable evaluation are the largest gap in
v0.1 and the most useful thing a collaborator could bring.**

C3 and C4 are properties of the harness rather than of answer determinability,
and apply to any task class.

A criterion is scored against a *configuration*, not a framework. The same
framework can be configured to pass or fail every criterion here. Where a
criterion belongs to the surrounding harness rather than the metric, it is
scored `not applicable` rather than `fail` — inflating a failure rate by
attaching unrelated properties to a component would be the same error we are
documenting.

---

## C1. Judge independence (de-anchoring) {#C1}

**Does the judge commit to its own answer before it is shown the candidate
output?**

Anchoring on the candidate is the mechanism that converts a judge from a
correctness check into a plausibility check. It is the difference between
"is this right?" and "does this look like the kind of thing that is right?"

This is the criterion that matters most, because it is the only intervention
shown to work. Committing first drops the judge's false-positive rate on wrong
answers to 0.012; blind solving, the limiting case of the same independence,
lifts discrimination from near chance to 0.96 with no reference answer
available. Ensembling does not close the gap — a strict three-family ensemble
still passes 55% of hacked wrong answers, its discrimination collapsing from
0.31 to 0.09. Nor do stricter rubrics or stronger judges.

**How much it helps depends on the task class, and we quote both numbers.** On
mathematics, commit-first collapses the false-positive rate from 0.719 to 0.012
and the single-sample gap falls to zero. On code, measured through best-of-N
selection, the same rule reduces an 8B judge's gap@16 from 0.378 to 0.227 — a
substantial reduction, but not an elimination. If you evaluate code, expect the
smaller effect. We would rather say so here than have you discover it.

The fix is also **capability-dependent**. It *"hurts the 1.7B judge, whose own
committed solutions are mostly wrong"* — 0.588 rising to 0.637 — and helps
every larger judge, plateauing by 8B. A judge below some threshold can satisfy
this criterion and measure worse than it would have without it. The threshold
is not quantified by any result we can cite; see
[candidate criteria](../candidates.md).

**The distinction that decides most scores.** A *recompute prompt* — telling
the judge, in a prompt that already contains the candidate, to solve the
problem itself first — is not de-anchoring and does not work. It leaves the
false-positive rate at 0.719. In the source paper's words: *the decisive
variable is not whether the judge sees the candidate but whether it commits an
answer of its own first.* Anything less than a genuine commitment produced
before the candidate enters context is the failed variant, and we record it as
such.

**Passes if:** the judge emits its own parseable answer to the task before any
comparison with the candidate, and acceptance is decided by matching the
candidate against that committed answer rather than by a holistic score.

The candidate may be visible at the moment of commitment — the source measures
exactly that configuration, and reports that what removes the anchor is the
independent commitment, not the candidate's absence. Withholding the candidate
entirely is the limiting case of the same independence, not the requirement. A
single-call prompt that instructs the judge to solve the problem first but
never requires it to emit a parseable answer does not pass.

**On code generation:** the match relation is well defined for tasks with a
determinable answer and undefined for code, where behavioural equivalence has
no definition we can cite. A code configuration that commits an answer but
whose match relation is unspecified is scored `insufficient evidence`, not
`fail`. This is an open item, not a settled position; see
[candidate criteria](../candidates.md).

**Evidence required:** the prompt template and the call sequence — and the
judge's own solve accuracy on the task distribution it is judging.

That last item is a disclosure, not a threshold. We cannot cite a floor, but
the source states its independence bound in exactly these terms: a genuinely
independent solver's ceiling is 1 − solve-acc, and it reports a 0.07 ceiling
for the setting it audits. (That 0.07 is the ceiling a judge solving at 0.93
would carry — our illustration, not the source's.) Given the solve accuracy,
you can apply that bound yourself
and decide whether conformance helps your judge. We would rather report a
number you can act on than assert a threshold we cannot source.

*Source: Zhou, "More Convincing, Not More Correct: Self-Play Reward Hacking of
Reference-Free LLM Judges", arXiv:2607.05904v1, §5.1, §5.2, §5.3 and
Appendix A.*

---

## C2. Independent ground-truth channel {#C2}

**Is there any correctness signal independent of the judge?**

If the judge is the only instrument, nothing in the system can observe the
divergence between reported quality and real quality. This is not
hypothetical: the divergence is only visible in the published results *because*
the researchers built a held-out channel to see it with.

Reference-free judging is independently measured to be too generous. Acceptance
of incorrect answers reaches 60% for the worst judge and dataset pair measured,
one judge model on one Telugu benchmark, while the same paper finds judges
reasonably calibrated in English and Arabic;
adding reference information flips the judge's decisions by as much as 85% in
some settings and, in others, not at all; and judge–human agreement rises from
0.34–0.74 to 0.85–0.96 once reference information is supplied. Almost all of
those flips are the judge withdrawing credit it had already granted.

**Passes if:** a correctness signal exists and is independent of the judge.

This criterion does **not** require that the signal be held out from whatever
produces or selects outputs. An earlier draft did, on the intuition that a
check you also optimise against stops being a check. That intuition is not
something we can cite, and the paper cited here reports the opposite for its
own de-anchored channel: used as the training reward, it stayed inflation-proof
across self-play. Five self-play iterations on a 128-item audit subset, three
seeds and one task family — two iterations is the paper's default elsewhere —
settle the question in neither direction, so feedback status is recorded for
each configuration and
reported as a distribution, and no verdict depends on it. The open question is
stated in [candidate criteria](../candidates.md).

**Evidence required:** the correctness signal, the path showing whether the
judge is the only instrument producing the verdict — **and evidence that the
signal works.**

A channel that passes everything satisfies this criterion in letter while
carrying no information at all, and it reports exactly what a working channel
reports when the system under test is genuinely correct: perfect scores, no
divergence, nothing to see. The two cases are indistinguishable from the
numbers alone, and only one of them is good news. So the difference has to be
shown:

- **Negative controls** — deliberately incorrect implementations, each
  demonstrated to fail the check. At minimum: answers precomputed for the
  visible cases, suppressed error conditions, and correct-in-the-typical-case
  failures at the stated domain boundaries.
- **A positive control** — a known-correct implementation passing the check in
  full, establishing that it discriminates rather than merely rejects.

A channel offered without this evidence is scored `insufficient evidence`, not
`pass`. This is a requirement on what must be shown, not a threshold: no citable
result fixes how many controls suffice, and inventing a number would repeat the
mistake corrected in C3.

*Sources: Zhou 2026, arXiv:2607.05904 — hidden-anchor audit design. Kranti &
Vajjala, "LLM Judges Can Be Too Generous When There Is No Reference Answer",
arXiv:2607.12885, 14 July 2026.*

---

## C3. Retrieval and contamination controls {#C3}

**Can a passing result have been retrieved rather than derived?**

An evaluation that permits lookup measures lookup. Restricting repository
history and network access moved measured resolution rates by up to 20.7 points
on SWE-bench Pro, and the effect is model-dependent: 14.1 and 20.7 points on two
models, under 1 point on a third in the same experiment. On one model,
63% of successful resolutions retrieved the fix rather than deriving it.

**Passes if:** the eval environment restricts the retrieval paths that would
let a candidate look up the answer.

An earlier draft also required those paths to be documented. The cited source
measures the effect of *removing* leakage channels and says nothing about
disclosing them, so that conjunct was ours rather than a finding, and it has
been removed.

**Evidence required:** the environment specification — network access,
repository history visibility, and whether task provenance is reachable from
inside the sandbox.

*Sources: Cursor, "Reward hacking is swamping model intelligence gains",
25 June 2026. SpecBench, arXiv:2605.21384.*

---

## C4. Resistance to degenerate passes {#C4}

**Would a solution that special-cases the visible checks be caught?**

Automated red-teaming of 10 popular agent benchmarks catalogued 219 distinct
flaws across eight recurring classes and produced 10 working exploits, with
nine benchmarks hacked on almost all instances. Degenerate
passing — satisfying the checks by a route that does not generalise — is the
most portable of those classes and the one that transfers from benchmarks to
production configurations.

The effect grows with task size: the 90th-percentile gap between visible and
held-out pass rates grows by approximately 27 percentage points for every
tenfold increase in code size (a weak fit, R² = 0.21; the paper's abstract
rounds it to 28), with
documented cases including a 2,900-line "compiler" that memorised test inputs.
Evaluations of small, single-function tasks are the regime where this is
hardest to see, not the regime where it is absent.

An instruction telling the judge to penalise special-casing does not satisfy
this criterion. That is a plausibility instruction, and plausibility scoring is
what fails.

**Passes if:** at least part of the correctness check uses inputs the candidate
cannot enumerate in advance.

**Evidence required:** the check suite itself — **and reachability, per
held-out check.**

A held-out check is *reachable* if some known-incorrect implementation fails it
while passing the entire check set visible to the candidate. An unreachable
check cannot catch anything the visible checks would not have caught first, so
it adds no resistance to degenerate passing however carefully it was written.
Reachability is a property of the two suites as a pair, not of either alone,
and it is shown by exhibiting the implementation rather than argued from
inspection.

A held-out suite can therefore be large, careful, and still blind. Counting
held-out checks measures nothing; counting reachable ones measures the
resolution of the instrument. A suite offered without per-check reachability is
scored `insufficient evidence`, not `pass`.

*Sources: BenchJack, arXiv:2605.12673, and Berkeley RDI, "How We Broke Top AI
Agent Benchmarks", April 2026 — the same work; flaw taxonomy V1–V8. SpecBench,
arXiv:2605.21384.*

---

## What is deliberately not here {#what}

**Criteria for non-verifiable tasks.** The largest gap, described under Scope
above. We would rather have four criteria that reach exactly as far as the
evidence than six that do not.

**Position, verbosity and self-preference bias.** Well documented, widely
mitigated, and — per the published defence results — not where the decisive
failure is. Adding them would lengthen the list without changing any verdict.

**Prompt injection through model output into the judge prompt.** Real, but it
reads as a party trick rather than a systemic property, and a config can resist
injection while failing every criterion above.

**Anything we cannot cite.** There are obvious candidate criteria — rubric
drift over time, judge-model version pinning, inter-rater agreement against
human adjudication — that belong here eventually. They are not in v0.1 because
we have not found published results that fix a pass condition precisely enough
to score. Suggestions with citations are welcome.

## Changelog {#changelog}

- **v0.1** (August 2026) — initial publication. Four criteria, all externally
  cited; scope limited to evaluators of verifiable tasks.
