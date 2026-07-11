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

# Does NOT use mdformat. Included as an idempotency smoke test against a
# real-world Obsidian vault (standard GFM task-list checkboxes).
#
# ryandeardorff/public-notes (src/site/notes/**/*.md) was evaluated and
# dropped: it surfaced a real dollarmath idempotency bug (indentation grows
# 2 spaces per format pass for `$$` blocks nested in list items) plus
# thousands of escape warnings from `[[wikilink]]` syntax, which needs the
# separate mdformat-wikilink extension (not installed here) to render
# correctly. Re-add once the dollarmath bug is fixed and wikilink is wired
# into the canary env's extensions.
REPOS: list[Repo] = [
    Repo("z3z1ma-vault", "https://github.com/z3z1ma/vault", ("notes/**/*.md",)),
]
