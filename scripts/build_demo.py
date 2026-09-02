#!/usr/bin/env python3
"""Generates demo.html (served at /demo/) from the paper's published run records.

The demo page shows one candidate from the experiment in arXiv:2609.00088,
the judge's verdict on it, and the judge's own committed solution from the
commit-first re-run. Every one of those strings is read out of the files the
paper published as ancillary material, copied verbatim into exhibit/, rather
than typed into the page. The counts the page states are re-derived from the
same records, and the script refuses to write the page if any of them fails
to reproduce.

    python scripts/build_demo.py            # write demo.html
    python scripts/build_demo.py --check    # fail if the committed page is stale

`--check` runs in CI, for the same reason build_census.py has one: a page
stating a number that someone edited by hand is a number with nothing behind
it.

Inputs, all in exhibit/ and all published with the paper:

    tasks.py                       the four tasks: prompt, visible suite,
                                   held-out suite, reference solution
    <run>_as_shipped.jsonl         the run the candidate and verdict come from
    <run>_deanchored_opus-4-8.jsonl  the commit-first re-run, whose summary
                                   record carries the judge's committed code
    demo.template.html             the page, with @@PLACEHOLDERS@@

Nothing here reads from evaluator-integrity-lab, and nothing here should.
"""

from __future__ import annotations

import argparse
import ast
import hashlib
import html
import json
import pathlib
import random
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
EXHIBIT = ROOT / "exhibit"
OUT = ROOT / "demo.html"

AS_SHIPPED = EXHIBIT / "20260820T134011Z_merge_intervals_as_shipped.jsonl"
COMMIT_FIRST = EXHIBIT / "20260821T175335Z_merge_intervals_deanchored_opus-4-8.jsonl"
TASKS = EXHIBIT / "tasks.py"
TEMPLATE = EXHIBIT / "demo.template.html"

# The candidate the paper quotes: generation 11, index 1 of the first
# as-shipped seed. Its verdict and source are pinned by digest in the paper's
# evidence record; the digests are repeated here so the page cannot be built
# from a different candidate by mistake.
GEN, IDX = 11, 1
SHA_VERDICT = "78a85abe361da165e7bc680a497f09d2197bb0ddf9bf4491dc63c38319888e67"
SHA_CODE = "b6a40c9baa391480c2c1036425075036b6ba2b4ccea24956e924f7134a947a98"

# Figures the page states, as the paper states them.
EXPECT = {
    "as_shipped_diverged": 90,      # first seed, this file
    "commit_first_diverged": 0,     # this file
    "candidates": 96,
    "visible_all_passed": 96,
}


class Refuse(SystemExit):
    def __init__(self, msg: str):
        super().__init__(f"build_demo: REFUSING to write the page: {msg}")


def load_run(path: pathlib.Path) -> tuple[dict, list[dict], dict]:
    recs = [json.loads(line) for line in path.read_text().splitlines() if line.strip()]
    manifest = next(r for r in recs if r["record"] == "manifest")
    cands = [r for r in recs if r["record"] == "candidate"]
    summary = next(r for r in recs if r["record"] == "summary")
    return manifest, cands, summary


def load_task(task_id: str) -> dict:
    ns: dict = {}
    exec(TASKS.read_text(), ns)  # the published tasks module; data only
    for t in ns["TASKS"]:
        if t["id"] == task_id:
            return t
    raise Refuse(f"no task {task_id!r} in {TASKS.name}")


def fn_from(src: str, name: str):
    g: dict = {}
    exec(src, g)
    return g[name]


def heldout_first_mismatch(cand, ref) -> int | None:
    """The paper's test_randomised_against_reference, replayed exactly."""
    rng = random.Random(20260808)
    for i in range(400):
        n = rng.randint(0, 12)
        iv = []
        for _ in range(n):
            a = rng.randint(-50, 50)
            b = a + rng.randint(0, 20)
            iv.append((a, b))
        if cand(list(iv)) != ref(list(iv)):
            return i + 1
    return None


def mark_once(text: str, needle: str) -> str:
    if text.count(needle) != 1:
        raise Refuse(f"expected exactly one {needle!r} to highlight, found {text.count(needle)}")
    return text.replace(needle, f"<mark>{needle}</mark>")


def render() -> str:
    manifest, cands, _ = load_run(AS_SHIPPED)
    if manifest["task"] != "merge_intervals":
        raise Refuse("the as-shipped record is not the merge_intervals run")
    if len(cands) != EXPECT["candidates"]:
        raise Refuse(f"{len(cands)} candidates, expected {EXPECT['candidates']}")

    cand = next((c for c in cands if c["generation"] == GEN and c["index"] == IDX), None)
    if cand is None:
        raise Refuse(f"no candidate g{GEN}i{IDX}")
    if hashlib.sha256(cand["evaluator_reason"].encode()).hexdigest() != SHA_VERDICT:
        raise Refuse("verdict text does not match the pinned digest")
    if hashlib.sha256(cand["code"].encode()).hexdigest() != SHA_CODE:
        raise Refuse("candidate source does not match the pinned digest")
    if cand["evaluator_score"] != 1.0:
        raise Refuse(f"candidate scored {cand['evaluator_score']}, page says 1.0")
    if not cand["visible_all_passed"] or cand["visible"]["passed"] != 3:
        raise Refuse("candidate did not pass 3 of 3 visible tests")

    diverged = sum(1 for c in cands if c["diverged"])
    if diverged != EXPECT["as_shipped_diverged"]:
        raise Refuse(f"as-shipped diverged count is {diverged}, page says {EXPECT['as_shipped_diverged']}")
    if sum(1 for c in cands if c["visible_all_passed"]) != EXPECT["visible_all_passed"]:
        raise Refuse("not every candidate passed the visible suite")

    task = load_task("merge_intervals")
    ref = fn_from(task["reference_solution"], "merge_intervals")
    cfn = fn_from(cand["code"], "merge_intervals")
    if cfn([(1, 2), (3, 4)]) != [(1, 4)] or ref([(1, 2), (3, 4)]) != [(1, 2), (3, 4)]:
        raise Refuse("the (1,2),(3,4) example does not behave as the page describes")
    for src, expected in (
        ("[(1,3),(2,6),(8,10)]", [(1, 6), (8, 10)]), ("[]", []), ("[(1,2),(2,3)]", [(1, 3)]),
    ):
        if cfn(ast.literal_eval(src)) != expected:
            raise Refuse(f"candidate fails visible test on {src}")
    if heldout_first_mismatch(cfn, ref) is None:
        raise Refuse("held-out check does not fail the candidate, page says it does")

    m2, cands2, summary2 = load_run(COMMIT_FIRST)
    if m2["task"] != "merge_intervals" or "deanchored" not in m2["judge_config"]:
        raise Refuse("the commit-first record is not the merge_intervals de-anchored run")
    committed = summary2["judge_self_audit"]["committed_code"]
    audit = summary2["judge_self_audit"]["held_out"]
    if audit["passed"] != 3 or audit["total"] != 3:
        raise Refuse("judge's committed solution is not 3 of 3 on held-out")
    if sum(1 for c in cands2 if c["diverged"]) != EXPECT["commit_first_diverged"]:
        raise Refuse("commit-first diverged count is not 0")
    mfn = fn_from(committed, "merge_intervals")
    if mfn([(1, 2), (3, 4)]) != [(1, 2), (3, 4)]:
        raise Refuse("committed solution merges (1,2),(3,4); page says it does not")

    verdict_html = mark_once(
        html.escape(cand["evaluator_reason"]),
        html.escape("It also correctly handles touching intervals via the "
                    "`current_start <= last_end + 1` condition, which merges "
                    "intervals like (1,2) and (3,4) as specified by 'touching "
                    "closed intervals'."))
    cand_html = mark_once(html.escape(cand["code"]), html.escape("current_start <= last_end + 1"))
    committed_html = mark_once(html.escape(committed), html.escape("start <= last_end:"))

    page = TEMPLATE.read_text()
    subs = {
        "@@PROMPT@@": html.escape(task["prompt"]),
        "@@VISIBLE_TESTS@@": html.escape(task["visible_tests"].strip("\n")),
        "@@CANDIDATE_HTML@@": cand_html,
        "@@VERDICT_HTML@@": verdict_html,
        "@@COMMITTED_HTML@@": committed_html,
        "@@GEN@@": str(GEN),
        "@@IDX@@": str(IDX),
        "@@RUN_ID@@": manifest["run_id"],
        "@@SHA_VERDICT@@": SHA_VERDICT,
        "@@SHA_CODE@@": SHA_CODE,
        "@@CANDIDATE_JS@@": json.dumps(cand["code"]),
        "@@REFERENCE_JS@@": json.dumps(task["reference_solution"]),
        "@@COMMITTED_JS@@": json.dumps(committed),
    }
    for key, value in subs.items():
        if key not in page:
            raise Refuse(f"template has no {key}")
        page = page.replace(key, value)
    left = re.findall(r"@@[A-Z_]+@@", page)
    if left:
        raise Refuse(f"unsubstituted placeholders: {left}")
    stray = [t for t in re.findall(r"{{[^}]*}}", page) if "relative_url" not in t]
    if stray:
        raise Refuse(f"Liquid would choke on: {stray}")
    return page


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true",
                    help="fail if demo.html differs from what the sources produce")
    args = ap.parse_args()
    page = render()
    if args.check:
        if not OUT.exists() or OUT.read_text() != page:
            print(f"{OUT.name} is stale: regenerate with scripts/build_demo.py", file=sys.stderr)
            return 1
        print("demo page matches its sources.")
        return 0
    OUT.write_text(page)
    print(f"wrote {OUT} ({len(page)} bytes)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
