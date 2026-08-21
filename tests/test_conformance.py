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
        "source_type": "framework_default_template",
        "source_url": "https://example.invalid",
        "collected": "2026-08-08", "task_class": "subjective",
        "stratum": "framework_default",
        "assessments": {
            "C1_de_anchoring": {"verdict": "fail", "evidence": "x", "judgement_call": False},
            "C2_ground_truth_channel": {"verdict": "fail", "evidence": "x", "judgement_call": False},
            "C3_retrieval_controls": {"verdict": "pass", "evidence": "x"},
            "C4_degenerate_pass_resistance": {"verdict": "pass", "evidence": "x"},
        },
    }
    assert any("out of scope" in p for p in validate([rec]))
    for cid in ("C1_de_anchoring", "C2_ground_truth_channel"):
        rec["assessments"][cid]["verdict"] = "not_applicable"
        rec["assessments"][cid]["not_applicable_reason"] = "task_class_out_of_scope"
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
    """POLICY: conformance/corpus/README.md -- non-publishable strata are
    "published **as aggregates only**, with no attribution"; and
    conformance/report.py's own docstring, "--public prints the aggregate form
    only".

    The disclosure policy as a test rather than a habit. This one caught a real
    leak: the first version of the wording-sensitive report block printed
    config identities into --public.
    """
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
    """POLICY: conformance/criteria.py -- "Every criterion is externally cited".

    This replaces a regex on the shape of the `citation` string. That check
    passed on "arXiv:0000.00000", and passed on a real citation whose numbers
    came from somewhere else; it was the degenerate pass C4 describes. The
    criterion now has to name a source in the registry, and that source has to
    be pinned.
    """
    from conformance.citations import CLAIMS, SOURCES_BY_ID
    from conformance.criteria import CRITERIA
    from conformance.verify_citations import pinning
    for c in CRITERIA:
        claims = [cl for cl in CLAIMS if cl.criterion_id == c.id]
        assert claims, f"{c.id}: no entry in the citation ledger"
        for cl in claims:
            src = SOURCES_BY_ID[cl.source]
            assert pinning(src.identifier) != "none", f"{c.id}: {src.id}"


def test_citation_chain_holds():
    """Every quantity in the criteria is tied to a source, and still matches."""
    from conformance.verify_citations import check
    assert not check()


def test_a_quantity_with_no_source_fails_the_build():
    """The property the chain exists for, exercised rather than assumed."""
    import dataclasses

    from conformance import verify_citations
    from conformance.criteria import CRITERIA

    bent = dataclasses.replace(CRITERIA[0], why=CRITERIA[0].why + " 0.4242.")
    monkey = [bent] + list(CRITERIA[1:])
    saved = verify_citations.CRITERIA
    verify_citations.CRITERIA = monkey
    try:
        problems = verify_citations.check()
    finally:
        verify_citations.CRITERIA = saved
    assert any("0.4242" in p for p in problems), problems


def test_editing_a_criterion_away_from_its_evidence_breaks_the_chain():
    """The link that makes the ledger more than a list kept alongside.

    C3's documentation conjunct and C2's held-out clause were both text that
    drifted off its citation with every check still green. A `supports` span is
    an exact substring of the criterion, so that drift now fails.
    """
    import dataclasses

    from conformance import verify_citations
    from conformance.citations import CLAIMS
    from conformance.criteria import CRITERIA_BY_ID

    claim = next(c for c in CLAIMS if c.status == "verified")
    crit = CRITERIA_BY_ID[claim.criterion_id]
    text = getattr(crit, claim.field).replace(claim.supports[0], "[rewritten]")
    bent = dataclasses.replace(crit, **{claim.field: text})
    saved = dict(verify_citations.CRITERIA_BY_ID)
    verify_citations.CRITERIA_BY_ID[crit.id] = bent
    try:
        problems = verify_citations.check()
    finally:
        verify_citations.CRITERIA_BY_ID.clear()
        verify_citations.CRITERIA_BY_ID.update(saved)
    assert any("SPAN NOT FOUND" in p for p in problems), problems


def test_publishing_mode_refuses_unread_citations():
    """POLICY: criteria/README.md, "Publishing a version" step 3 --
    "evidence that has not been re-verified is not published".

    The ledger is mostly unverified today, so this asserts the refusal fires
    rather than asserting a clean run. When every claim is verified this test
    is the one that says so, by starting to fail.
    """
    from conformance.verify_citations import main
    assert main(["--require-sources", "--json"]) == 1


def test_unsupported_claims_stay_visible():
    """A claim the source contradicts is a finding against our own text.

    It must not be quietly demoted to "unverified", where it would read as
    merely unread. The report names it and the count is printed every run.
    """
    from conformance.citations import CLAIMS
    unsupported = [c for c in CLAIMS if c.status == "unsupported"]
    for c in unsupported:
        assert c.quote, f"{c.criterion_id}: unsupported with no counter-quote"
        assert c.note, f"{c.criterion_id}: unsupported with no explanation"


def test_published_prose_agrees_with_derived_figures():
    """The weak link in published_figures.json, closed.

    The mechanism only binds numbers that are IN the file. Nothing stopped a
    sentence in the published criteria from quoting a count that had since
    moved. This scans the published prose for "<n> of <m>" claims and requires
    each to match a pair the corpus actually derives.
    """
    from conformance.report import load_corpus, derive_figures
    fig = derive_figures(load_corpus(CORPUS))
    pairs = {(fig["c1_pass"], fig["records_in_c1_scope"]),
             (fig["recompute_variants"], fig["records_in_c1_scope"]),
             (fig["reference_supplied"], fig["reference_supplied_of"]),
             (fig["framework_default_in_scope"], fig["records_total"])}
    # Only claims about OUR population. A denominator we never publish belongs
    # to a cited external result -- "10 of 10 audited benchmarks" is BenchJack's
    # finding, not ours, and must pass through untouched.
    ours = {m for _, m in pairs}
    for md in (ROOT / "criteria").rglob("*.md"):
        for n, m in re.findall(r"\b(\d{1,3}) of (\d{1,3})\b", md.read_text()):
            if int(m) not in ours:
                continue
            assert (int(n), int(m)) in pairs, (
                f"{md.relative_to(ROOT)} publishes '{n} of {m}', which the "
                f"corpus does not derive. Either the corpus moved and the "
                f"prose is now false, or the claim was never checked.")


def test_evidence_is_not_stale():
    from conformance.report import load_corpus, check_evidence_freshness
    assert not check_evidence_freshness(load_corpus(CORPUS))


def test_staleness_check_actually_fires():
    """A deadline nobody has tested is a deadline that will not fire."""
    from datetime import date
    from conformance.report import load_corpus, check_evidence_freshness
    recs = load_corpus(CORPUS)
    assert check_evidence_freshness(recs, today=date(2030, 1, 1))


def test_only_the_publishable_stratum_is_accepted():
    from conformance.report import STRATA
    assert STRATA == ("framework_default",)


def _probe(**over):
    rec = {
        "_file": "probe.json", "config_id": "probe/x",
        "source_type": "framework_default_template",
        "source_url": "https://example.invalid", "collected": "2026-08-08",
        "task_class": "verifiable", "stratum": "framework_default",
        "assessments": {
            "C1_de_anchoring": {"verdict": "fail", "evidence": "x", "judgement_call": False},
            "C2_ground_truth_channel": {"verdict": "fail", "evidence": "x", "judgement_call": False},
            "C3_retrieval_controls": {"verdict": "not_applicable", "evidence": "x",
                                      "not_applicable_reason": "harness_scope"},
            "C4_degenerate_pass_resistance": {"verdict": "fail", "evidence": "x", "judgement_call": False},
        },
    }
    rec.update(over)
    return rec


def test_not_applicable_requires_a_recorded_reason():
    """'Did not apply' and 'never came up' read the same in an aggregate."""
    from conformance.report import validate
    assert not validate([_probe()])
    rec = _probe()
    del rec["assessments"]["C3_retrieval_controls"]["not_applicable_reason"]
    assert any("not_applicable_reason" in p for p in validate([rec]))
    rec["assessments"]["C3_retrieval_controls"]["not_applicable_reason"] = "because"
    assert any("not_applicable_reason" in p for p in validate([rec]))


def test_a_record_asserting_nothing_does_not_pass():
    """The wholesale not_applicable hole: four blanks used to validate clean."""
    from conformance.report import validate
    rec = _probe()
    for a in rec["assessments"].values():
        a["verdict"] = "not_applicable"
        a["not_applicable_reason"] = "harness_scope"
    problems = validate([rec])
    assert any("asserts nothing" in p for p in problems), problems


def test_every_not_applicable_in_the_corpus_states_why():
    from conformance.report import load_corpus, NA_REASONS
    for r in load_corpus(CORPUS):
        for cid, a in r["assessments"].items():
            if a["verdict"] == "not_applicable":
                assert a.get("not_applicable_reason") in NA_REASONS, \
                    f"{r['config_id']}/{cid}"


def test_never_evaluated_criteria_are_named_as_such():
    """POLICY: criteria/README.md and the C5 dissolution in candidates.md --
    a criterion nothing was scored against has produced no finding, and must
    not be presented as though it had.

    Asserts the structural property, not the wording. An earlier version of
    this test asserted the exact sentences report.py prints, which is the
    report agreeing with itself: it would pass on any prose and fail on a typo,
    telling you nothing about whether the policy held.
    """
    import contextlib, io, sys
    import conformance.report as R
    from conformance.report import load_corpus, aggregate

    agg = aggregate(load_corpus(CORPUS))
    never = [a["title"] for a in agg.values() if a["scored"] == 0]
    assert never, "expected at least one never-evaluated criterion (C3)"

    argv = sys.argv
    sys.argv = ["report", "--public", "--corpus", CORPUS]
    try:
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            R.main()
        out = buf.getvalue()
    finally:
        sys.argv = argv

    for title in never:
        # Named somewhere other than the aggregate table row.
        assert out.count(title) >= 2, f"{title} is never called out as unevaluated"
        # And never given a percentage, which is what a rate would look like.
        for line in out.splitlines():
            if title in line and "%" in line:
                raise AssertionError(
                    f"{title} was evaluated 0 times but is shown with a rate: {line!r}")

    # Every not_applicable reason present in the corpus is accounted for in the
    # output, so a reader can tell a scoping judgement from a question that
    # never arose.
    reasons = {a.get("not_applicable_reason")
               for r in load_corpus(CORPUS)
               for a in r["assessments"].values()
               if a["verdict"] == "not_applicable"}
    for reason in reasons:
        assert reason in out, f"not_applicable_reason {reason!r} not surfaced"


def test_wording_sensitive_flags_surface_in_the_report():
    """A warning in a free-text note is a warning nothing can act on."""
    import contextlib, io, sys
    import conformance.report as R
    from conformance.report import load_corpus
    flagged = [r["config_id"] for r in load_corpus(CORPUS)
               for a in r["assessments"].values()
               if isinstance(a, dict) and a.get("wording_sensitive")]
    assert flagged, "expected at least one wording_sensitive record"

    def run(*extra):
        argv = sys.argv
        sys.argv = ["report", "--corpus", CORPUS, *extra]
        try:
            buf = io.StringIO()
            with contextlib.redirect_stdout(buf):
                R.main()
            return buf.getvalue()
        finally:
            sys.argv = argv

    # Default form carries the identities, so a reviewer knows what to re-read.
    private = run()
    assert "Wording-sensitive verdicts" in private
    for cid in flagged:
        assert cid in private

    # Public form carries the count and the criterion, never the identity --
    # the same disclosure rule the rest of the report obeys.
    public = run("--public")
    assert "Wording-sensitive verdicts" in public
    for cid in flagged:
        assert cid not in public, f"--public leaked {cid!r}"
