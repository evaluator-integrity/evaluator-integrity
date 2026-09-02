---
layout: main
title: "Evaluator Integrity"
description: "Your AI system can pass its evaluator and still be wrong. Evaluator Integrity tests the LLM judges and evaluation pipelines AI teams rely on, before their scores become release, procurement or assurance evidence."
---

<!--
  Site index. Order: the problem, the demo, the published evidence, what we
  do, who it is for, the invitation, then the research surface and contact.
  Every number here is either in arXiv:2609.00088 or in the census, and the
  two are labelled separately because they were taken on different dates.
-->

<p class="kicker">Evaluator auditing · London</p>

# Your AI system can pass its evaluator and still be wrong.

<p class="lede">Evaluator Integrity tests the LLM judges and evaluation
pipelines that AI teams rely on — before their scores become release,
procurement or assurance evidence.</p>

<p class="ctas">
  <a class="cta" href="{{ '/demo/' | relative_url }}">See the failure in 60 seconds &rarr;</a>
  <a class="cta cta-2" href="#contact">Have an evaluator checked</a>
</p>

<div class="exhibit">
  <p class="exhibit-h">From the paper &middot; recorded 20 August 2026</p>
  <p>A search with no access to correct answers was pointed at a shipped
  LLM judge, configured exactly as its documentation recommends. The judge
  read a broken interval-merging function, found the line that makes it
  wrong, and wrote:</p>
  <blockquote class="verdict">&ldquo;It also correctly handles touching
  intervals via the <code>current_start &lt;= last_end + 1</code> condition,
  which merges intervals like (1,2) and (3,4) as specified by
  &lsquo;touching closed intervals&rsquo;.&rdquo;</blockquote>
  <p>(1,2) and (3,4) do not touch. The function merges them anyway. The judge
  scored it <strong>1.0 out of 1.0</strong> and cited the bug as the reason.
  <a href="{{ '/demo/' | relative_url }}">Run the function yourself and watch it
  happen.</a></p>
</div>

<h2 id="findings">What the evidence says</h2>

<div class="stats">
  <p class="stat"><b>0 of 24</b><span>shipped judge configurations, across eight
  frameworks, implement the one defence the literature finds effective
  <em>(paper, August 2026)</em></span></p>
  <p class="stat"><b>90 &amp; 93 of 96</b><span>candidates that failed a held-out
  test the search could not see, yet were accepted by a documented judge
  configuration — two seeds <em>(paper)</em></span></p>
  <p class="stat"><b>0 of 96</b><span>such candidates under the commit-first
  defence, both seeds — and on a second task the same defence made things
  worse <em>(paper)</em></span></p>
  <p class="stat"><b>0 of 25</b><span>in-scope configurations that pass the
  first criterion, across 28 defaults from 10 packages <em>(living census,
  updated as packages are scored)</em></span></p>
</div>

<p>The paper is <a href="https://arxiv.org/abs/2609.00088">arXiv:2609.00088</a>.
Every number in it can be re-derived from the run records and replication
code published alongside it. The census counts differ from the paper's
because the census keeps growing after the paper was frozen; both are
correct at their dates.</p>

<h2 id="what">What Evaluator Integrity does</h2>

<p>We test evaluators. Not models — the instruments that score them: LLM
judges, grading rubrics, model-graded test harnesses, and the pipelines that
combine them. An evaluator is a measurement, and a measurement that the thing
being measured can influence is not one. Our work is finding out whether
yours can be, before someone else does.</p>

<p>An <strong>evaluator review</strong> takes one evaluator configuration and
the task it scores. We score the configuration against the
<a href="{{ '/criteria/v0.1/' | relative_url }}">published criteria</a>, then run
an ordinary optimisation loop against it the way the paper did — no
jailbreaks, no prompt injection, the loop production systems run every day —
and report what it accepted that it should not have, with the evidence. We
are doing a small number of these in 2026, with teams whose evaluator scores
decide something that matters.</p>

<p>We do not build or sell evaluation pipelines and will not. Testing an
evaluator requires independence from whoever sells it. The criteria are
open; the assessment against them is the work.</p>

<h2 id="who">Who this is for</h2>

<p>Teams whose evaluator scores gate a release, select a model, or tune an
agent — especially in coding, finance, legal, health and compliance, where a
confidently wrong output is expensive. Assurance, procurement and insurance
teams who are asked to accept an evaluation score as evidence and want to
know what it is evidence of. And maintainers of evaluation frameworks who
would rather hear about a default from us than from an incident.</p>

<h2 id="contact">Could this affect your team?</h2>

<div class="invite">
  <p>Send one evaluator prompt or configuration and one sentence on what its
  scores decide. We will reply with what we would test and why — that reply
  is free and specific, and it is the start of every review we do.</p>
  <p><a class="cta" href="mailto:idilgozel@evaluatorintegrity.com?subject=Evaluator%20review&body=What%20the%20evaluator%20scores%3A%0A%0AWhat%20decision%20depends%20on%20the%20score%3A%0A%0AThe%20prompt%20or%20configuration%20(paste%20or%20attach)%3A%0A">Email Idil &rarr;</a>
  <span class="invite-note">idilgozel@evaluatorintegrity.com</span></p>
</div>

<h2 id="research">Research, criteria and census</h2>

<ul class="research">
  <li><a href="https://arxiv.org/abs/2609.00088">The paper</a> — the audit
  of shipped judge configurations, the controlled experiment, and the
  finding that commit-first judging inherits the judge's own errors.
  Run records and replication code are published as ancillary files.</li>
  <li><a href="{{ '/criteria/v0.1/' | relative_url }}">Criteria v0.1</a> — four
  requirements an evaluator has to meet before its scores mean anything,
  each drawn from a published result and citing it, with stable anchors
  (<code>#C1</code>–<code>#C4</code>). Frozen on 25 August 2026; corrections
  appear as a new version.</li>
  <li><a href="{{ '/census/' | relative_url }}">Configuration census</a> — every
  framework default we have scored, each verdict resting on a quote from an
  artifact pinned by digest.</li>
  <li><a href="https://github.com/idilgozel/evaluator-integrity">Repository</a>
  — the corpus, the scorer, and the checks that re-verify both.</li>
</ul>

<p class="muted">If a criterion is wrong, we want to know. The largest gap
in v0.1 is non-verifiable evaluation — summarisation quality, helpfulness,
tone — where no published result is precise enough to fix a pass condition.
Write to the address above.</p>

<h2 id="founder">Founder</h2>

<p>Evaluator Integrity is run by Idil Gozel in London. Her research at UCL
is on reinforcement learning under partial observability: what a system
learns to do when it is rewarded through a signal it can only partly see,
and can influence. This company is that problem in production.</p>

<style>
  .ctas { display: flex; flex-wrap: wrap; gap: 0.7rem; margin: 1.6rem 0 2.6rem; }
  .exhibit {
    border: 1px solid var(--rule-strong); border-left: 4px solid var(--accent);
    background: var(--panel); border-radius: 6px;
    padding: 1.4rem 1.6rem 1.5rem; margin: 0 0 1rem;
  }
  .exhibit p:last-child { margin-bottom: 0; }
  .exhibit-h {
    font-family: var(--mono); font-size: 0.7rem; letter-spacing: 0.14em;
    text-transform: uppercase; color: var(--accent); margin: 0 0 0.8rem;
  }
  .verdict {
    margin: 1rem 0; padding: 0.8rem 1rem; border-left: 0;
    background: var(--paper); border: 1px solid var(--rule); border-radius: 4px;
    color: var(--ink); font-size: 0.98rem;
  }
  .stats { display: grid; gap: 1.2rem 1.6rem; margin: 1.6rem 0 1.4rem; }
  @media (min-width: 40rem) { .stats { grid-template-columns: 1fr 1fr; } }
  .stat { margin: 0; padding: 1rem 1.1rem; border: 1px solid var(--rule);
          border-radius: 6px; background: var(--panel); }
  .stat b { display: block; font-size: 1.9rem; line-height: 1.1;
            letter-spacing: -0.03em; margin-bottom: 0.35rem; }
  .stat span { display: block; font-size: 0.92rem; color: var(--muted); line-height: 1.45; }
  .stat em { font-style: normal; font-family: var(--mono); font-size: 0.72rem; }
  .invite {
    border: 1px solid var(--rule-strong); border-radius: 6px;
    padding: 1.4rem 1.6rem 1.5rem; margin: 1.4rem 0 1rem; background: var(--panel);
  }
  .invite p:last-child { margin-bottom: 0; }
  .invite-note { display: block; margin-top: 0.7rem; font-family: var(--mono);
                 font-size: 0.82rem; color: var(--muted); }
  @media (min-width: 34rem) { .invite-note { display: inline; margin-left: 0.9rem; } }
  .research li { margin-bottom: 0.7rem; }
</style>
