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
REPOS: list[Repo] = [
    Repo("z3z1ma-vault", "https://github.com/z3z1ma/vault", ("notes/**/*.md",)),
    # Real-world Obsidian/Dataview vault exercising dollarmath (incl. `$$`
    # nested in list items and blockquotes), wikilinks, and YAML/Dataview
    # frontmatter.
    Repo(
        "ryandeardorff-public-notes",
        "https://github.com/ryandeardorff/public-notes",
        ("src/site/notes/**/*.md",),
    ),
]
