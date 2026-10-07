"""Tests for the public-safety guard.

The guard is the thing standing between the lab material and a permanent public
record, so it gets tested like it matters. Two properties:

  * It fires on every category of private material it claims to catch.
  * It does not fire on this repository as it stands -- a guard that cries wolf
    gets bypassed, and a bypassed guard protects nothing.
"""

from __future__ import annotations

import importlib.util
import json
import re
import stat
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent


def _load_guard():
    """scripts/ is not a package, so load the module by path."""
    path = REPO_ROOT / "scripts" / "check_public_safe.py"
    spec = importlib.util.spec_from_file_location("check_public_safe", path)
    module = importlib.util.module_from_spec(spec)
    # Register before executing: @dataclass resolves annotations via
    # sys.modules[cls.__module__], which is absent for a module loaded by path.
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


guard = _load_guard()


# ---------------------------------------------------------------------------
# The repository as it stands
# ---------------------------------------------------------------------------


def test_repository_is_currently_clean():
    """The guard must pass on this repository. If this fails, either something
    private has landed or the guard has a false positive -- both are urgent."""
    assert guard.run(staged=False) == 0


def test_denylist_file_exists_and_loads():
    """The denylist is part of the guard. If it goes missing, the guard must
    refuse to run rather than quietly skip a check."""
    assert isinstance(guard.load_denylist(), list)


# ---------------------------------------------------------------------------
# Check 1 -- forbidden paths
# ---------------------------------------------------------------------------


def _stated_forbidden_dirs() -> set[str]:
    """The directory names POLICY.md's 'Never in this repository' section names.

    Parsed from the policy rather than retyped, so the policy statement is the
    single source and a test cannot drift away from it silently.
    """
    section = (REPO_ROOT / "POLICY.md").read_text()
    section = section.split("## Never in this repository")[1].split("\n##")[0]
    return set(re.findall(r"`([a-z-]+)/`", section))


def test_guard_forbids_exactly_what_the_policy_names():
    """POLICY: POLICY.md, 'Never in this repository'.

    The list existed in three places -- the policy prose, the guard's tuple,
    and this test -- with nothing checking they agreed. Adding a directory to
    the policy would have left the guard unchanged and every test still green.
    """
    assert _stated_forbidden_dirs() == set(guard.FORBIDDEN_DIR_NAMES), (
        "POLICY.md and scripts/check_public_safe.py disagree about which "
        "directories are forbidden. The policy is authoritative; update the "
        "guard."
    )


@pytest.mark.parametrize("name", sorted(guard.FORBIDDEN_DIR_NAMES))
def test_every_forbidden_directory_is_caught(name):
    """Derived from the guard's own list, so a new entry is covered on arrival."""
    findings = guard.check_paths([f"{name}/whatever.md"])
    assert findings, f"{name}/ should have been refused"
    assert findings[0].heading == "Private directory"


@pytest.mark.parametrize(
    "path",
    [
        "conformance/corpus-private/acme.json",  # nested under a real tree
        "notes/strategy/pricing.md",  # nested, not just top level
        "DEMO/index.html",  # case-insensitive
    ],
)
def test_forbidden_directories_are_caught_at_any_depth_or_case(path):
    findings = guard.check_paths([path])
    assert findings, f"{path} should have been refused"
    assert findings[0].heading == "Private directory"


@pytest.mark.parametrize(
    "path",
    [
        "criteria/v0.1/index.md",
        "conformance/report.py",
        "conformance/corpus/langchain-default.json",
        "README.md",
        "self-check/README.md",
    ],
)
def test_legitimate_paths_are_not_caught(path):
    assert guard.check_paths([path]) == []


def test_filename_alone_does_not_trip_the_directory_check():
    """'demo' as a filename is not 'demo/' as a directory."""
    assert guard.check_paths(["criteria/demo.md"]) == []


# ---------------------------------------------------------------------------
# Check 2 -- strata
# ---------------------------------------------------------------------------


def _record(**overrides):
    base = {"stratum": "framework_default", "criteria_version": "0.1"}
    base.update(overrides)
    return json.dumps(base)


def test_framework_default_record_is_allowed():
    findings = guard.check_records("conformance/corpus/ok.json", _record())
    assert findings == []


@pytest.mark.parametrize(
    "stratum", ["customer_configured", "internal", "pilot", "", "Framework_Default"]
)
def test_other_strata_are_refused(stratum):
    findings = guard.check_records(
        "conformance/corpus/x.json", _record(stratum=stratum)
    )
    assert any(f.heading == "Non-publishable corpus stratum" for f in findings)


def test_missing_stratum_fails_closed():
    text = json.dumps({"criteria_version": "0.1", "score": 3})
    findings = guard.check_records("conformance/corpus/x.json", text)
    assert any(f.heading == "Corpus record with no stratum" for f in findings)


# ---------------------------------------------------------------------------
# Check 3 -- client / engagement fields
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("field", ["client", "engagement", "Client", "ENGAGEMENT"])
def test_engagement_fields_are_refused(field):
    findings = guard.check_records(
        "conformance/corpus/x.json", _record(**{field: "whoever"})
    )
    assert any(
        f.heading == "Engagement material in a corpus record" for f in findings
    )


def test_engagement_field_nested_inside_a_wrapper_is_still_caught():
    text = json.dumps(
        {"stratum": "framework_default", "meta": {"provenance": {"client": "whoever"}}}
    )
    findings = guard.check_records("conformance/corpus/x.json", text)
    assert any(
        f.heading == "Engagement material in a corpus record" for f in findings
    )


def test_record_inside_a_list_is_checked():
    text = json.dumps([_record_dict(), {"stratum": "internal"}])
    findings = guard.check_records("conformance/corpus/x.json", text)
    assert any(f.heading == "Non-publishable corpus stratum" for f in findings)


def _record_dict():
    return {"stratum": "framework_default"}


# ---------------------------------------------------------------------------
# Record identification and parsing
# ---------------------------------------------------------------------------


def test_underscore_prefixed_files_are_templates_not_records():
    assert not guard.is_corpus_record("conformance/corpus/_TEMPLATE.json")


def test_json_outside_a_corpus_directory_is_not_a_record():
    assert not guard.is_corpus_record("site/package.json")


def test_corpus_json_and_jsonl_are_records():
    assert guard.is_corpus_record("conformance/corpus/a.json")
    assert guard.is_corpus_record("conformance/corpus/a.jsonl")


def test_jsonl_records_are_checked_line_by_line():
    text = _record() + "\n" + json.dumps({"stratum": "internal"}) + "\n"
    findings = guard.check_records("conformance/corpus/x.jsonl", text)
    assert any(f.heading == "Non-publishable corpus stratum" for f in findings)


def test_unparseable_record_is_refused_not_ignored():
    findings = guard.check_records("conformance/corpus/x.json", "{not json")
    assert any(f.heading == "Unreadable corpus record" for f in findings)


# ---------------------------------------------------------------------------
# Check 4 -- denylist
# ---------------------------------------------------------------------------


def test_denylist_matches_file_contents():
    findings = guard.check_denylist(
        "criteria/v0.1/index.md", "scored for Acme Corp in June", ["acme corp"]
    )
    assert findings and findings[0].heading == "Denylisted string"


def test_denylist_matches_the_path_itself():
    findings = guard.check_denylist(
        "conformance/corpus/acme-corp.json", None, ["Acme Corp"]
    )
    assert findings and findings[0].heading == "Denylisted string"


def test_denylist_is_case_insensitive():
    assert guard.check_denylist("a.md", "ACME CORP", ["acme corp"])


@pytest.mark.parametrize(
    "slug", ["acme-corp.json", "acme_corp.md", "Acme.Corp.txt", "acme--corp/x.md"]
)
def test_denylist_matches_slugified_and_punctuated_forms(slug):
    """A client name reaches a repository as a filename far more often than as
    prose, and it arrives slugified when it does."""
    assert guard.check_denylist(slug, None, ["Acme Corp"])


def test_normalisation_does_not_make_everything_match():
    assert guard.check_denylist("readme.md", "unrelated prose", ["Acme Corp"]) == []


def test_denylist_does_not_fire_on_unrelated_text():
    assert guard.check_denylist("a.md", "nothing to see", ["acme corp"]) == []


def test_guard_and_denylist_are_exempt_from_content_scanning():
    """Otherwise every denylist term would match the file listing it."""
    assert "scripts/denylist.txt" in guard.SELF_EXEMPT
    assert "scripts/check_public_safe.py" in guard.SELF_EXEMPT


# ---------------------------------------------------------------------------
# Failure reporting
# ---------------------------------------------------------------------------


def test_failure_message_explains_why_not_just_what(capsys):
    guard.report(guard.check_paths(["strategy/positioning.md"]), scope="staged")
    output = capsys.readouterr().out
    assert "strategy/positioning.md" in output
    assert "Why this matters" in output
    assert "What to do" in output
    assert "--no-verify" in output  # tells them not to reach for it


def test_working_tree_failure_warns_that_history_may_be_affected(capsys):
    guard.report(guard.check_paths(["outreach/emails.md"]), scope="worktree")
    output = capsys.readouterr().out
    assert "history" in output.lower()


def test_history_failure_does_not_tell_the_reader_to_delete_the_file(capsys):
    """POLICY: POLICY.md -- "Making this repository public exposes its history,
    not its current state ... There is no undo."

    The worktree wording ("this material is already in the working tree") is
    wrong for a history finding and actively misleading: the file may not be
    in the working tree at all, and deleting it would not help if it were.
    """
    guard.report(guard.check_paths(["outreach/emails.md"]), scope="history")
    output = capsys.readouterr().out
    assert "already in the working tree" not in output
    assert "IN HISTORY" in output
    assert "rewritten" in output.lower()


# ---------------------------------------------------------------------------
# History mode -- the check that still works after a leak is committed
# ---------------------------------------------------------------------------


def test_history_mode_finds_what_the_working_tree_scan_cannot(tmp_path):
    """A leak committed and then deleted is invisible to every other mode.

    This is the whole reason history mode exists, so it is exercised against a
    real repository rather than asserted. Without it, --history could scan
    nothing at all and still report clean.
    """
    import subprocess

    repo = tmp_path / "r"
    repo.mkdir()

    def git(*args):
        subprocess.run(["git", *args], cwd=repo, check=True,
                       capture_output=True)

    git("init", "-q")
    git("config", "user.email", "t@t")
    git("config", "user.name", "t")
    (repo / "README.md").write_text("fine\n")
    git("add", "README.md")
    git("commit", "-q", "-m", "first")

    leak = repo / "strategy"
    leak.mkdir()
    (leak / "pricing.md").write_text("tiers\n")
    git("add", "strategy/pricing.md")
    git("commit", "-q", "-m", "plant")
    git("rm", "-q", "strategy/pricing.md")
    git("commit", "-q", "-m", "delete again")

    saved = guard.REPO_ROOT
    guard.REPO_ROOT = repo
    try:
        # The leak is gone from the working tree ...
        assert guard.run(staged=False) == 0
        # ... and still in history.
        assert guard.run_history() == 1
    finally:
        guard.REPO_ROOT = saved


# ---------------------------------------------------------------------------
# Wiring -- a hook that is not installed does nothing
# ---------------------------------------------------------------------------


def test_pre_commit_hook_exists_and_is_executable():
    hook = REPO_ROOT / ".githooks" / "pre-commit"
    assert hook.exists(), "the pre-commit hook is missing"
    assert hook.stat().st_mode & stat.S_IXUSR, "the hook is not executable"


def test_pre_commit_hook_runs_the_guard_in_staged_mode():
    hook = (REPO_ROOT / ".githooks" / "pre-commit").read_text()
    assert "check_public_safe.py" in hook
    assert "--staged" in hook


def test_ci_runs_the_guard():
    ci = (REPO_ROOT / ".github" / "workflows" / "ci.yml").read_text()
    assert "scripts/check_public_safe.py" in ci


# ---------------------------------------------------------------------------
# Cross-module agreement
# ---------------------------------------------------------------------------


def test_guard_and_scorer_agree_on_the_publishable_stratum():
    """POLICY: conformance/corpus/README.md, 'Only `stratum: framework_default`.'

    Two modules decide this independently -- the guard refuses a commit, the
    scorer validates a record -- and nothing checked they named the same
    stratum. A divergence would mean the validator accepting exactly what the
    guard rejects, which teaches a contributor the wrong rule at the point they
    are trying to follow it.
    """
    from conformance.report import STRATA

    assert STRATA == (guard.PUBLISHABLE_STRATUM,)
