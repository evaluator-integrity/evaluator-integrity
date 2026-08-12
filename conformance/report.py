"""Scores the corpus against the criteria and aggregates the results.

    python -m conformance.report                 # aggregate table
    python -m conformance.report --check         # CI: validate + re-derive
    python -m conformance.report --public        # redacted: no config identities
    python -m conformance.report --json          # machine-readable
    python -m conformance.report --scope-note    # what v0.1 does and does not reach

Scope note, because this is where the two repositories differ most: the lab
harness scores every stratum. This module publishes individual records for
`framework_default` only -- what a framework ships with by default, which is
already public -- and everything else as an aggregate with no attribution.

`--check` is wired into CI and does two things. It validates every record, and
it re-derives every published figure from the committed corpus and compares
against `conformance/published_figures.json`. It exits non-zero when a published
number can no longer be reproduced from the evidence, so a result drifting away
from its evidence breaks the build rather than sitting there looking
authoritative.

`--public` is not a courtesy, it is the disclosure policy implemented in code,
so that publishing the wrong form takes deliberate effort.
"""

from __future__ import annotations

import argparse
import glob
import json
import os
import sys
from collections import Counter

from conformance.criteria import (CRITERIA, CRITERIA_BY_ID, SCOPE_NOTE,
                                  TASK_CLASSES, VERDICTS, VERSION, applies)

CORPUS_DIR = "conformance/corpus"

REQUIRED = ("config_id", "source_type", "source_url", "collected",
            "task_class", "stratum", "assessments")
STRATA = ("framework_default", "public_config")
SOURCE_TYPES = (
    "framework_default_template",
    "framework_documentation_example",
    "public_repo_config",
    "vendor_published_config",
)


def load_corpus(path: str = CORPUS_DIR) -> list[dict]:
    records = []
    for f in sorted(glob.glob(os.path.join(path, "*.json"))):
        if os.path.basename(f).startswith("_"):
            continue
        with open(f) as fh:
            rec = json.load(fh)
        rec["_file"] = f
        records.append(rec)
    return records


def validate(records: list[dict]) -> list[str]:
    problems = []
    seen = set()
    for r in records:
        f = r.get("_file", "?")
        for k in REQUIRED:
            if k not in r:
                problems.append(f"{f}: missing required field {k!r}")
        cid = r.get("config_id")
        if cid in seen:
            problems.append(f"{f}: duplicate config_id {cid!r}")
        seen.add(cid)
        if r.get("source_type") not in SOURCE_TYPES:
            problems.append(
                f"{f}: source_type {r.get('source_type')!r} not in {SOURCE_TYPES}")
        tc = r.get("task_class")
        if tc not in TASK_CLASSES:
            problems.append(f"{f}: task_class {tc!r} not in {TASK_CLASSES}")
        if r.get("stratum") not in STRATA:
            problems.append(f"{f}: stratum {r.get('stratum')!r} not in {STRATA}")
        for crit_id, a in (r.get("assessments") or {}).items():
            if crit_id not in CRITERIA_BY_ID:
                problems.append(f"{f}: unknown criterion {crit_id!r}")
                continue
            if a.get("verdict") not in VERDICTS:
                problems.append(
                    f"{f}/{crit_id}: verdict {a.get('verdict')!r} not in {VERDICTS}")
            if not a.get("evidence"):
                problems.append(
                    f"{f}/{crit_id}: no evidence recorded. Every verdict needs "
                    f"the quote, line, or config fragment it rests on.")
            if tc in TASK_CLASSES and not applies(crit_id, tc) \
                    and a.get("verdict") not in ("not_applicable",
                                                 "insufficient_evidence"):
                problems.append(
                    f"{f}/{crit_id}: task_class is {tc!r}, so this criterion is "
                    f"out of scope for v0.1 and must be not_applicable. "
                    f"Scoring it would extend the evidence past where it goes.")
            if a.get("verdict") == "fail" and not a.get("judgement_call") in (True, False):
                problems.append(
                    f"{f}/{crit_id}: set judgement_call true/false so contested "
                    f"calls can be re-reviewed.")
        missing = set(CRITERIA_BY_ID) - set(r.get("assessments") or {})
        if missing:
            problems.append(f"{f}: unscored criteria {sorted(missing)}")
    return problems


def count_recompute_variants(records: list[dict]) -> int:
    """Configs that ATTEMPT the fix but implement the version shown not to work.

    A separate number, and a good one: "n configs try to de-anchor and use the
    recompute prompt, which leaves the false-positive rate at 0.719" is a
    sharper finding than a bare failure count.
    """
    return sum(
        1 for r in records
        if (r.get("assessments", {}).get("C1_de_anchoring", {}) or {})
        .get("recompute_variant") is True
    )


def count_reference_supplied(records: list[dict]) -> tuple[int, int]:
    """Configs that hand the judge a reference answer.

    A secondary number worth reporting on its own. Supplying a reference
    materially improves judge accuracy (agreement 0.34-0.74 -> 0.85-0.96,
    arXiv:2607.12885) but does not create an independent channel, so these
    still fail C2. Reporting both keeps the failure count honest.
    """
    scored = [r for r in records
              if (r.get("assessments", {}).get("C2_ground_truth_channel", {}) or {})
              .get("verdict") in ("pass", "fail")]
    n = sum(1 for r in scored
            if (r["assessments"]["C2_ground_truth_channel"] or {})
            .get("reference_supplied") is True)
    return n, len(scored)


FIGURES_PATH = "conformance/published_figures.json"


def derive_figures(records: list[dict]) -> dict:
    """Every number this project publishes, computed from the corpus alone.

    If a figure appears in the criteria, the write-up, a preprint or a
    consultation response, it belongs here. Anything not derivable from the
    committed corpus is not a finding, it is an assertion.
    """
    agg = aggregate(records)
    c1 = agg["C1_de_anchoring"]
    ref_n, ref_total = count_reference_supplied(records)
    fw = [r for r in records
          if r.get("stratum") == "framework_default"
          and (r.get("assessments", {}).get("C1_de_anchoring", {}) or {})
          .get("verdict") in ("pass", "fail")]
    return {
        "records_total": len(records),
        "records_in_c1_scope": c1["scored"],
        "c1_pass": c1["pass"],
        "c1_fail": c1["fail"],
        "recompute_variants": count_recompute_variants(records),
        "reference_supplied": ref_n,
        "reference_supplied_of": ref_total,
        "framework_default_in_scope": len(fw),
        "frameworks": sorted({r.get("framework", "?") for r in records}),
    }


def check_published_figures(records: list[dict]) -> list[str]:
    if not os.path.exists(FIGURES_PATH):
        return [f"{FIGURES_PATH} is missing. Published figures must be "
                f"committed so CI can re-derive them; without it a number in "
                f"the write-up has nothing holding it to the evidence."]
    with open(FIGURES_PATH) as f:
        published = json.load(f)
    derived = derive_figures(records)
    out = []
    for k, v in published.items():
        if k.startswith("_"):
            continue
        if k not in derived:
            out.append(f"published figure {k!r} is no longer computed at all")
        elif derived[k] != v:
            out.append(
                f"published figure {k!r} no longer follows from the corpus: "
                f"published {v!r}, corpus now gives {derived[k]!r}. Either the "
                f"corpus changed and everything quoting this number must be "
                f"updated, or the change is a mistake.")
    return out


def aggregate(records: list[dict]) -> dict:
    out = {}
    for c in CRITERIA:
        counts = Counter(
            (r.get("assessments", {}).get(c.id, {}) or {}).get("verdict",
                                                               "insufficient_evidence")
            for r in records
        )
        scored = counts["pass"] + counts["fail"]
        out[c.id] = {
            "title": c.title,
            "citation": c.citation,
            "pass": counts["pass"],
            "fail": counts["fail"],
            "not_applicable": counts["not_applicable"],
            "insufficient_evidence": counts["insufficient_evidence"],
            "scored": scored,
            "conformance_rate": (counts["pass"] / scored) if scored else None,
        }
    return out


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--corpus", default=CORPUS_DIR)
    p.add_argument("--check", action="store_true")
    p.add_argument("--public", action="store_true")
    p.add_argument("--json", action="store_true")
    p.add_argument("--scope-note", action="store_true",
                   help="print the v0.1 scope statement (what these criteria "
                        "do and do not reach)")
    args = p.parse_args()

    records = load_corpus(args.corpus)
    problems = validate(records)

    if args.check:
        problems = problems + check_published_figures(records)
        if problems:
            print(f"{len(problems)} problem(s):", file=sys.stderr)
            for x in problems:
                print("  -", x, file=sys.stderr)
            return 1
        print(f"corpus ok: {len(records)} records, all criteria scored")
        print("published figures re-derived from the corpus and match")
        return 0

    if problems:
        print(f"{len(problems)} corpus problem(s):", file=sys.stderr)
        for x in problems:
            print("  -", x, file=sys.stderr)

    agg = aggregate(records)
    if args.json:
        print(json.dumps({"version": VERSION, "n": len(records),
                          "criteria": agg}, indent=2))
        return 0

    by_stratum = {}
    for r in records:
        by_stratum.setdefault(r.get("stratum", "?"), []).append(r)
    by_class = {}
    for r in records:
        by_class.setdefault(r.get("task_class", "?"), []).append(r)

    print(f"Framework v{VERSION} conformance -- N = {len(records)} configurations")
    print("  strata:      " + ", ".join(
        f"{k} {len(v)}" for k, v in sorted(by_stratum.items())))
    print("  task class:  " + ", ".join(
        f"{k} {len(v)}" for k, v in sorted(by_class.items())) + "\n")
    print(f"{'criterion':<38} {'pass':>5} {'fail':>5} {'n/a':>5} {'?':>3}  rate")
    print("-" * 68)
    for cid, a in agg.items():
        rate = "  --" if a["conformance_rate"] is None else f"{a['conformance_rate']*100:5.1f}%"
        print(f"{a['title']:<38} {a['pass']:>5} {a['fail']:>5} "
              f"{a['not_applicable']:>5} {a['insufficient_evidence']:>3}  {rate}")

    ref_n, ref_total = count_reference_supplied(records)
    if ref_total:
        print(f"\nOf the {ref_total} configurations in C1/C2 scope, {ref_n} hand "
              f"the judge a reference answer. That materially improves judge "
              f"accuracy but does not create a second instrument, so they still "
              f"fail C2.")

    rc = count_recompute_variants(records)
    if rc:
        print(f"\nOf the C1 failures, {rc} attempt the fix and implement the "
              f"recompute variant, which leaves the false-positive rate at 0.719.")

    # Honesty guard: a criterion every record lands identically on carries no
    # discriminating information. Say so rather than presenting 0% as though
    # the number separated good configs from bad ones.
    flat = [a["title"] for a in agg.values()
            if a["scored"] and (a["pass"] == 0 or a["fail"] == 0)]
    if flat:
        print(f"\nNote: every scored configuration lands the same way on "
              f"{'; '.join(flat)}. Report these as findings about the "
              f"population ('no configuration in the corpus did X'), not as "
              f"rates that discriminate between configurations.")

    c1 = agg.get("C1_de_anchoring", {})
    if c1.get("scored"):
        print(
            f"\nHeadline: the intervention that drops judge false positives on "
            f"wrong answers to 0.012 -- where the obvious cheaper fix, a "
            f"recompute prompt, leaves them at 0.719 -- has been public since "
            f"July 2026; "
            f"{c1['pass']} of {c1['scored']} shipped configurations implement it."
        )
        fw = [r for r in records
              if r.get("stratum") == "framework_default"
              and (r.get("assessments", {}).get("C1_de_anchoring", {}) or {})
              .get("verdict") in ("pass", "fail")]
        if fw:
            fw_pass = sum(
                1 for r in fw
                if r["assessments"]["C1_de_anchoring"]["verdict"] == "pass")
            print(f"Of the framework defaults and documented examples in scope "
                  f"-- the templates teams copy -- {fw_pass} of {len(fw)} "
                  f"implement it.")

    if args.scope_note:
        print(SCOPE_NOTE)

    if not args.public and records:
        print("\nPer-config detail (PRIVATE -- do not publish; see Brief v2 §6):")
        for r in records:
            fails = [k for k, v in (r.get("assessments") or {}).items()
                     if v.get("verdict") == "fail"]
            print(f"  {r['config_id']:<40} fails: {', '.join(fails) or 'none'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
