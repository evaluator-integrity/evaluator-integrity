# Self-check

A ten-minute self-assessment a team can run against their own evaluator, without
tooling and without talking to anyone.

TODO(port): the check items themselves, derived from criteria C1–C4 once those
are ported. The design rule below is settled and constrains whatever lands here.

## Design rule: it can tell you that you fail. It can never tell you that you pass.

The self-check outputs **a findings list, never a score.**

Where it finds something, it says so. Where it finds nothing, it says:

> No failure detected by this check. **This is not a pass.**

and it says that every time, in the output itself — not in a footnote, not in
documentation the reader has already closed.

### Why the asymmetry is real and not modesty

Ten minutes of unverified self-inspection has enough evidence to find a defect
and never enough to establish the absence of one. Those are different claims
with different evidential burdens, and the gap between them does not close by
looking harder for ten minutes.

Finding a defect needs one instance. You look at the judge prompt, the failure
is there, you have it. The finding stands on its own and does not depend on how
thorough the search was.

Concluding there is no defect needs coverage — evidence that you looked
everywhere a defect could be, that you would have recognised one, and that the
thing you inspected is the thing actually running. A self-check has none of
that. It inspects what the team already knows to look at, judged by the people
who built it, against no pinned artifact. Absence of evidence is doing all the
work, and it is not up to the job.

So the honest output where nothing is found is "this check found nothing", which
is a fact about the check. "Your evaluator is sound" is a claim about the
evaluator, and nothing in the preceding ten minutes supports it.

### Why a score would damage the project specifically

A score is a portable claim. It gets extracted from context immediately —
"4/4 on Evaluator Integrity" in a slide, a vendor questionnaire, a procurement
response — and it arrives at the reader stripped of the fact that its subject
issued it about themselves after ten minutes.

Two consequences, both bad:

**It cannibalises certification.** Certification's entire value is that an
independent party checked. A free self-issued number that looks like the same
claim substitutes for it — not because anyone is deceived, but because the
cheaper artefact is good enough for the box that needed ticking. The paid
verification is then competing with a free counterfeit of its own output.

**It undermines the standard.** Self-issued scores circulate, some are wrong,
and the criteria get the blame — they become the thing people scored themselves
4/4 against, which is an argument *against* trusting them. A standard for
evaluation integrity that hands out unverified self-assessments has failed at
its own subject matter, and that failure is legible to exactly the audience it
most needs to convince.

A findings list carries none of this. "The self-check surfaced three issues" is
not a credential, cannot be quoted as one, and has no counterfeit value.

### What follows from the rule

- **No numeric output. No pass/fail verdict. No badge, no certificate, no
  shareable artefact of any kind.** If it can be screenshotted as an
  achievement, it is the wrong output.
- **Findings phrased as observations with a pointer**, not as scored criteria.
  Each one names the criterion it relates to (`C1`–`C4`) so the reader can go to
  the criteria text, which is where actual assessment happens.
- **No self-reported results are collected or published** anywhere under this
  project's name. An unverified self-report published as a finding is the exact
  failure mode the criteria exist to detect.
- **A clean run is a prompt to go further**, not a conclusion. Where it finds
  nothing, the check ends by pointing at the full criteria and at what a real
  assessment requires that this one cannot: pinned artifacts, quoted evidence,
  and someone other than the author.

### Still open

**Whether ten minutes survives contact with C1–C4.** If the four criteria cannot
honestly be self-inspected in ten minutes, the answer is a longer check, not a
thinner one. Ten minutes is a target for how much attention this is worth
asking for, not a constraint that content gets trimmed to fit.

## Licence and versioning

Prose and criteria material: CC BY 4.0, written to be quoted. If this ever
carries a version number that people cite, it comes under the same freezing
policy as the criteria — see [`../criteria/README.md`](../criteria/README.md).
