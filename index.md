---
layout: default
title: "Evaluator Integrity"
---

<!--
  Site index. The site publishes the criteria and the corpus behind them,
  and nothing else. See site/README.md.
-->

# Evaluator Integrity

Criteria for auditing the automated evaluators that AI teams use to score
their own systems.

These criteria do not assess model quality. They assess the instrument that
measures it: the LLM judges, test harnesses, and configurations that produce
the scores teams act on. Each criterion is drawn from a published result and
cites its source, so the criteria are only as strong as the work behind them
— which you can go and read.

## Read

- **[Criteria v0.1](criteria/v0.1/)** — four criteria, each with a stable
  anchor (`#C1`–`#C4`) so a single criterion can be cited on its own.
  Published 25 August 2026 and frozen; corrections appear as a new version.
- **[Configuration census](census/)** — 27 evaluator configurations shipped
  as framework defaults, scored against v0.1, with the evidence behind each
  verdict.
- **[Candidate criteria](criteria/candidates.html)** — requirements that
  look plausible but lack a published result precise enough to fix a pass
  condition. Nothing on that page is scored, and none of it should be cited
  as a requirement.

## Check

You do not have to take a score on trust. Every census record names the
artifact it was scored from, pinned by package digest rather than version
string, and quotes the text the verdict rests on. The criteria are held to
the same standard: every quantity C1–C4 state is recorded against the
published result it came from and re-read out of that source before
publication.

The [repository](https://github.com/idilgozel/evaluator-integrity) carries
the corpus, the scorer, and the checks that re-verify both.

## Cite

Cite the versioned path, which is frozen and always resolves:

    criteria/v0.1/index.md#C2

Avoid `criteria/latest` in anything durable — that path is repointed when a
new version publishes, and is meant for browsing.

## Criticism

If a criterion is wrong, unmeasurable, or missing, we want to know.
The largest gap in v0.1 is criteria for non-verifiable evaluation —
summarisation quality, helpfulness, tone — and a collaborator who could
help close it would be welcome.

---

Criteria and prose are CC BY 4.0; the code is Apache-2.0. Written by
Idil Gozel, Evaluator Integrity, London.
