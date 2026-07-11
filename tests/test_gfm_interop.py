"""Regression tests for interop with mdformat-gfm's task list rule.

See: https://github.com/KyleKing/mdformat-obsidian/issues/11

Both plugins register a markdown-it core rule via
``md.core.ruler.after("inline", ...)``, so which one runs first depends on
the order extensions are registered in, not just insertion. Standard GFM
checkboxes must render unescaped regardless of that order, while extended
Obsidian marks must keep working.
"""

from __future__ import annotations

import mdformat
import pytest

_INPUT = "- [ ] open task\n- [x] done task\n- [X] DONE TASK\n- [/] partial\n- [-] cancelled\n"
_EXPECTED = "- [ ] open task\n- [x] done task\n- [x] DONE TASK\n- [/] partial\n- [-] cancelled\n"


@pytest.mark.parametrize(
    "extensions",
    [
        ["obsidian", "gfm", "tables"],
        ["gfm", "tables", "obsidian"],
    ],
    ids=["obsidian-registered-first", "gfm-registered-first"],
)
def test_standard_checkboxes_not_escaped_with_gfm(extensions):
    """Standard GFM marks must be left to mdformat-gfm regardless of plugin registration order."""
    output = mdformat.text(_INPUT, extensions=extensions)
    assert output == _EXPECTED


def test_extended_marks_still_work_without_gfm():
    output = mdformat.text(_INPUT, extensions=["obsidian"])
    assert output == _INPUT
