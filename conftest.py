"""Put the repository root on `sys.path` for the test suite.

WHY THIS FILE EXISTS, because an empty-looking conftest invites deletion.

The suite imports two things from the repository: `conformance`, which is a
declared package, and `scripts.build_census`, which is deliberately NOT one
(pyproject declares `packages = ["conformance"]`, because scripts/ holds
build tooling rather than shipped library code).

Whether those imports resolve depended entirely on how pytest was invoked:

    python -m pytest tests/     # works -- `python -m` prepends CWD
    pytest tests/               # ModuleNotFoundError: No module named 'scripts'

CI runs the second form. Every developer here had been running the first, so
a suite that could not import half of what it tests looked green locally and
failed only after the repository went public -- 30 of 84 tests erroring on
import, which is the failure mode this project exists to document: a check
that reports success while verifying nothing.

pytest inserts the directory of a rootdir conftest.py into `sys.path` under
its default import mode, so this file makes both invocations equivalent. It
must stay at the repository root; moving it into tests/ inserts tests/
instead and changes nothing.
"""
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).parent.resolve()))
