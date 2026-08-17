---
title: "Evaluator Integrity — Candidate Criteria"
---

# Candidate criteria

**Nothing on this page is a criterion.** Nothing here is scored, nothing here
has a stable anchor id, and nothing here should be cited as a requirement. This
is the holding area for requirements that are plausible but not yet supported
by a published result precise enough to fix a pass condition.

A candidate leaves this page in one of two directions: it acquires a citation
that settles it and becomes a numbered criterion in a new version, or the
evidence goes against it and it stays here with that written down. Neither
outcome is a failure. Publishing a requirement we cannot cite would be.

Each entry states what the requirement would be, the argument for it, the
evidence against it if any, and — the part that decides its future — what
observation would settle the question.

---

## Held-out ground-truth channel {#held-out}

*Moved here from C2's pass condition, 17 August 2026.*

**The requirement, as it stood.** A correctness signal satisfies C2 only if it
is "demonstrably not fed back into generation or selection". The published text
justified this with the assertion that "a ground-truth check that is also used
to select or train against stops being ground truth".

**The argument for it.** It is the Goodhart argument, and it is intuitive: a
measure optimised against ceases to measure. If the held-out suite becomes a
training signal, the next model is selected partly for passing it, and the
independence that made it worth having is spent.

**The evidence against it.** The paper C2 cites reports the opposite for its own
de-anchored channel:

> "Used as the training reward, the de-anchored channel keeps the false-positive
> rate at zero across self-play, preventing the basin rather than only detecting
> it."

> "The same reference-free channel that audits the basin is, in our experiments,
> an effectively inflation-proof training reward."

— Zhou 2026, arXiv:2607.05904v1, abstract and §5.2.

What degrades under optimisation in that work is the *plausibility-judge* reward
and the *ensemble* reward. An independent exact-match channel does not: the
oracle control that rewards exact match instead of the judge "shows no
inflation".

**Why it is here rather than narrowed.** Those results are two iterations at
n=128 on one task family. They do not establish that feedback is safe, and they
are more than enough to show that our clause was not established either.
Narrowing the requirement to fit them would replace an over-read with a smaller
over-read. So the clause is removed rather than qualified, and the question is
recorded as open.

**What would settle it.** A measurement of an independent correctness channel's
false-positive rate under sustained optimisation — more iterations than two,
more than one task family, and ideally a horizon long enough for selection
pressure to accumulate. If the channel degrades, the held-out requirement
becomes a criterion with a citation. If it holds up at scale, C2 is right as it
now stands and this entry closes.

**Meanwhile.** Feedback status is recorded for each configuration and published
as a distribution. No verdict depends on it. A reader who believes the Goodhart
argument can apply it to the distribution themselves; we are declining to score
it, not declining to report it.

---

## C5 — Audit-channel validation {#C5}

*Held here rather than published, 17 August 2026. Ported from
`criteria-c5-draft-v1.md`.*

**Has the independent check been demonstrated to fail implementations that are
known to be wrong?**

C2 requires a correctness signal independent of the judge. It does not require
that signal to work. A held-out suite that passes everything satisfies C2 in
full while carrying no information at all — and it reports exactly what a
functioning suite reports when the system under test is genuinely correct:
perfect scores, no divergence, nothing to see. The two cases are
indistinguishable from the numbers alone, and only one of them is good news.

This is the failure the rest of the framework documents, moved one level up.
C1 says do not trust a judge because it reports success. C5 says do not trust
the instrument you built to check the judge, for the same reason. An audit
channel is an evaluator; it is subject to the criteria it is used to enforce.

**The two errors are not symmetric, and only one is dangerous.** An audit
channel that is *too generous* — silent on a requirement the specification
states — undercounts divergence. It costs sensitivity and it cannot manufacture
a finding. Wrong, but in the safe direction. An audit channel that is *stricter
than the specification* — enforcing a property the system under test was never
asked to satisfy — manufactures divergence out of nothing. An output that fails
such a check is not evidence of a gamed evaluator; it is evidence of an unstated
requirement, and a judge scoring that output highly is the judge behaving
**correctly**. Reporting it as evaluator failure inverts the finding while
leaving every number intact.

**Reachability.** A held-out check is *reachable* if some known-incorrect
implementation fails it while passing the entire check set visible to the
system under test. An unreachable held-out check contributes nothing: nothing
can fail it without having already failed something visible, so it cannot
detect a divergence the visible checks would not have caught first.
Reachability is a property of the two suites as a pair, not of either alone,
and it is demonstrated by exhibiting the implementation rather than argued from
inspection.

The corollary is that a held-out suite can be large, careful, and still blind.
Counting held-out checks measures nothing; counting reachable ones measures the
resolution of the instrument.

**Would pass if** all four hold:

1. **Negative controls.** A published set of deliberately incorrect
   implementations, each demonstrated to fail the held-out check. The set
   covers at least: answers precomputed for the visible cases, suppressed error
   conditions, and correct-in-the-typical-case failures at the stated domain
   boundaries.
2. **Positive control.** A known-correct implementation passes the held-out
   check in full — establishing that the suite discriminates rather than merely
   rejects.
3. **Reachability.** Every held-out check is demonstrated reachable, or is
   declared unreachable and excluded from the reported measure.
4. **Specification traceability.** Every held-out check traces to a stated
   requirement in the specification given to the system under test. A check
   with no such line is removed, or the requirement is added to the
   specification before any measurement is taken.

**Evidence that would be required:** the negative-control implementations;
their per-check outcomes against both the visible and the held-out suite; the
reachability table; and, for each held-out check, the specification line it
enforces.

### Why it is not a criterion

**Its proposed citation does not hold.** The draft rested C5 on BenchJack /
Berkeley RDI, on the reading that defective benchmark ground truth is among the
documented flaw classes, and flagged that the reading had not been checked
against the pinned quotes. It has now been checked, and it fails twice over.

The eight classes are named in Figure 6a of arXiv:2605.12673v1: V1 Isolation,
V2 Answers in test, V3 RCE, V4 LLM judge, V5 Weak match, V6 Logic gaps, V7
Trust untrusted, V8 Excess perms. None of them is defective ground truth. V2 is
the nearest and is a different failure — answers *reachable* ("test splits with
publicly available ground truth"), not answers *wrong* — and reachable-but-
correct ground truth is already C3's territory.

The draft also described that work as finding exploits on "10 of 10 audited
benchmarks". The paper reports 10 working exploits across 10 audited
benchmarks, describes near-perfect scores on "most of the benchmarks", and its
Figure 5 caption says "nine benchmarks are hacked on almost all of instances".
That claim is separately recorded as unsupported.

**The second argument survives and is the one to decide.** C5 makes no new
empirical claim. It states a necessary condition for C2 and C4 to be scoreable
at all, and both are already cited — on that reading C5 is a hygiene criterion
rather than an evidential one. That argument does not depend on BenchJack and
is untouched by the finding above. It is also a departure from this project's
stated rule that every criterion is externally cited, and it should be made
deliberately and in public rather than by omission.

**Its precondition needs restating.** The draft scopes C5 with
`applies_when="C2_ground_truth_channel == pass"`. That should become a
self-contained factual predicate about the configuration — *where an
independent correctness channel exists* — rather than a reference to how
another criterion scored. A verdict dependency couples C5's meaning to C1–C4's
definitions across versions: revise C2's pass condition in a later version and
C5's scope moves with it, though C5's own text never changed. Published
versions are frozen so a citation keeps its meaning, and a criterion whose
meaning is a function of its neighbours cannot offer that.

A predicate also keeps it scoreable. Gated on a verdict, C5 would read
`not applicable` on all 27 records by construction, since no criterion in this
corpus passes anything — publishing as "n/a 27" without ever having been
evaluated once.

---

## C1 match relation for code generation {#c1-match-code}

*Open item, 17 August 2026.*

C1 accepts a configuration when the judge emits a parseable answer of its own
and acceptance is decided by **matching** the candidate against it. For a task
with a determinable answer, matching is exact-match and the criterion is
scoreable as written. For code generation it is undefined: two programs can be
behaviourally equivalent and textually unlike, and no source we cite defines
the equivalence relation.

The intervention itself is evidenced on code — Zhou §5.3 applies commit-first
to a code pool and reports the 8B judge's gap@16 falling from 0.378 to 0.227 —
so narrowing C1's scope to determinable-answer tasks would discard evidence we
have. What §5.3 does not supply is a matching procedure. It uses held-out
unit-test execution as the *anchor* for measuring truth, which is C2's
territory, not C1's match relation.

Candidate definitions exist — the candidate passes the tests the judge
committed, or differential agreement on held-out inputs — and adopting either
without a citation would repeat the defect that produced C3's documentation
conjunct.

**Interim position.** A code configuration that commits an answer but leaves
the match relation unspecified is scored `insufficient evidence`, not `fail`.
No configuration in the current corpus is affected, because none commits an
answer at all; this binds prospectively, on the first de-anchored code judge
anyone builds, which is precisely what C1 recommends they build.

**What would settle it.** A published result that fixes a behavioural-
equivalence relation for judge-committed code precisely enough to score, or a
measurement of commit-first on code under a stated match relation with the
relation reported.

---

## Judge-capability floor for C1 conformance {#c1-capability-floor}

*Open item, 17 August 2026.*

C1 conformance may be counterproductive below some judge capability. Zhou §5.3
reports that the commit-first fix "is capability-dependent in exactly the
direction the independence bound predicts": it *"hurts the 1.7B judge, whose
own committed solutions are mostly wrong"*, moving its gap from 0.588 to 0.637,
and "helps every larger judge, plateauing by 8B".

The implication is uncomfortable and worth stating plainly: a configuration can
satisfy C1's letter — committing a parseable answer, accepting only on a match
— and measure *worse* than the same configuration that did not conform,
because the standard it now matches against is mostly wrong. A criterion that
can be satisfied to the detriment of the thing it protects needs a floor.

**The threshold is unquantified.** The source shows the direction and two
endpoints — harmful at 1.7B, plateauing by 8B — on one judge family, one task
pool, one budget. Parameter count is a poor proxy for the quantity that
actually matters, which is the judge's own solve accuracy on the task it is
judging. Zhou's own independence bound is stated in those terms: the ceiling
for a genuinely independent solver is 1 − solve-acc, which is 0.07 for a judge
solving at 0.93.

**What would settle it.** A measurement of commit-first benefit against judge
solve accuracy across several families and task classes, sufficient to state a
floor as a solve-accuracy threshold rather than a model size. Until then C1
carries the caveat in its `why` and no verdict depends on capability.
