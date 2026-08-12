"""Tests that protect the study, not the code.

Each of these guards a property the published result depends on. If one fails,
something quoted in public has stopped following from the evidence.
"""
import json
import pathlib
import re

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[1]
CORPUS = str(ROOT / "conformance" / "corpus")


def test_corpus_validates():
    from conformance.report import load_corpus, validate
    recs = load_corpus(CORPUS)
    assert recs, "no corpus records found"
    assert not validate(recs)


def test_published_figures_follow_from_the_corpus():
    """The one that matters: every number we publish is re-derived here."""
    from conformance.report import load_corpus, check_published_figures
    assert not check_published_figures(load_corpus(CORPUS))


def test_scope_is_enforced_not_remembered():
    """A subjective-task config may not be scored on C1/C2."""
    from conformance.report import validate
    rec = {
        "_file": "probe.json", "config_id": "probe/subjective",
        "source_type": "public_repo_config", "source_url": "https://example.invalid",
        "collected": "2026-08-08", "task_class": "subjective",
        "stratum": "public_config",
        "assessments": {
            "C1_de_anchoring": {"verdict": "fail", "evidence": "x", "judgement_call": False},
            "C2_ground_truth_channel": {"verdict": "fail", "evidence": "x", "judgement_call": False},
            "C3_retrieval_controls": {"verdict": "pass", "evidence": "x"},
            "C4_degenerate_pass_resistance": {"verdict": "pass", "evidence": "x"},
        },
    }
    assert any("out of scope" in p for p in validate([rec]))
    rec["assessments"]["C1_de_anchoring"]["verdict"] = "not_applicable"
    rec["assessments"]["C2_ground_truth_channel"]["verdict"] = "not_applicable"
    assert not validate([rec])


def test_every_verdict_carries_evidence():
    from conformance.report import load_corpus
    for r in load_corpus(CORPUS):
        for cid, a in r["assessments"].items():
            assert a.get("evidence"), f"{r['config_id']}/{cid} has no evidence"


def test_every_record_has_artifact_provenance():
    """No verdict may rest on a link. Links drift; digests do not."""
    from conformance.provenance import ARTIFACTS_BY_CONFIG
    from conformance.report import load_corpus
    for r in load_corpus(CORPUS):
        assert r["config_id"] in ARTIFACTS_BY_CONFIG, r["config_id"]
        for k in ("artifact", "artifact_path", "artifact_sha256"):
            assert r.get(k), f"{r['config_id']} missing {k}"
        assert len(r["artifact_sha256"]) == 64, r["config_id"]


def test_public_report_never_names_configs():
    """The disclosure policy, as a test rather than a habit."""
    import contextlib, io, sys
    import conformance.report as R
    from conformance.report import load_corpus
    recs = load_corpus(CORPUS)
    argv = sys.argv
    sys.argv = ["report", "--public", "--corpus", CORPUS]
    try:
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            R.main()
        out = buf.getvalue()
    finally:
        sys.argv = argv
    for r in recs:
        assert r["config_id"] not in out, f"--public leaked {r['config_id']!r}"


def test_criteria_module_and_published_doc_agree():
    """criteria.py scores; the markdown is cited. They are one definition."""
    from conformance.criteria import CRITERIA
    doc = (ROOT / "criteria" / "v0.1" / "index.md").read_text()
    for c in CRITERIA:
        short = c.id.split("_", 1)[0]
        assert f"{{#{short}}}" in doc, f"{c.id}: no stable anchor in the published doc"
        assert c.title.split(" (")[0] in doc, f"{c.id}: title out of sync"


def test_every_criterion_is_externally_cited():
    """The rule the framework rests on: no criterion we invented ourselves."""
    from conformance.criteria import CRITERIA
    for c in CRITERIA:
        assert re.search(r"(arXiv:\d|20\d\d)", c.citation), c.id
