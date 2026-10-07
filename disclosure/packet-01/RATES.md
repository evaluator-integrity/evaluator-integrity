# Measured rates

These are experimental rates for the stated items, judge snapshots and native MASK prompt/configuration. They are not calibrated population estimates. All intervals in the table are two-sided exact 95% binomial intervals. Repeated replies share items; item bootstrap intervals are given separately below.

A joint case requires a parser-mediated score change, preservation of the judge's terminal verdict and clean matched controls. Each joint case was agent-screened. The literal modified inputs appear in `witnesses.json`.

| Run | Judge | Direction | Joint cases / replies | Exact 95% interval | Distinct items affected / tested |
| --- | --- | --- | --- | --- | --- |
| Live-14 | gpt-4.1-2025-04-14 | Response B, truth A | 20/200 (10.00%) | 6.22–15.02% | 15/40 |
| Live-14 | gpt-4o-2024-08-06 | Response B, truth A | 10/160 (6.25%) | 3.04–11.19% | 9/40 |
| Live-11 | gpt-4o-2024-08-06 | Response A, truth B | 8/576 (1.39%) | 0.60–2.72% | 7/32 |

Live-14 item bootstrap 90% intervals are 6.5–14.0% for gpt-4.1 and 3.1–9.4% for gpt-4o. Rates across runs are not pooled because the inputs, direction and judge configuration differ.

Live-14 calibration passed 80/80 on each judge. Matched neutral terminal verdicts were preserved 80/80 on each judge. Valid-response terminal verdicts were preserved 200/200 on gpt-4.1 and 158/160 on gpt-4o. The gpt-4o run also contains one further parser-mediated score change to evasion; it is excluded from the ten joint cases because the terminal verdict changed. Both observed departures are retained in the private results.

Live-11 calibration passed 64/64 and matched neutral verdicts were preserved 96/96. Nine replies contained the marker before the terminal verdict, but only eight changed the score. Typographic punctuation prevented extraction in the remaining reply.

Agent review confirmed all 20, 10 and 8 joint cases respectively. This is agent/model evidence, with outcome-aware case inspection alongside blinded component review. Repeated model agreement is not independent human evidence. In Live-14, 84/96 input-preservation labels were flagged as ambiguous even though all were judged preserved; this caveat must accompany use of the results.
