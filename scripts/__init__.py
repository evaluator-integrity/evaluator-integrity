"""Not a library -- this exists so tests can import the build scripts.

`scripts/` holds command-line tools, and they stay runnable as plain scripts.
The package marker is here because scripts/build_census.py generates a
published page, and a generator whose output nothing re-derives is a generator
whose output drifts. The test imports it rather than shelling out so a failure
reports as a test failure rather than a non-zero exit code.

_config.yml excludes scripts/ from the site build, so nothing here is
published.
"""
