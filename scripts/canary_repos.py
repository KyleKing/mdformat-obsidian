"""Canary repos for 'scripts/canary.py': real downstream repos to idempotency-check.

This file is project-specific and is NOT overwritten by 'copier update' (see
'_skip_if_exists' in copier.yml). Canary testing is entirely opt-in: leave
REPOS empty to skip it, or add entries for real-world repos that exercise
'obsidian' syntax.

To update an entry: run
`git -C .tox/canary/cache/<name> show HEAD:.pre-commit-config.yaml` and check
for a mdformat hook plus its args/excludes, then mirror them here so canary
tracks what the downstream repo actually formats.

Example entry::

    Repo(
        "some-project",
        "https://github.com/some-org/some-project",
        ("docs/**/*.md",),
        excludes=("docs/changelog.md",),
        options={"wrap": 120},
    )
"""

from __future__ import annotations

from canary import Repo

REPOS: list[Repo] = []
