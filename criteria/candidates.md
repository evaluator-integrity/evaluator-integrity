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
