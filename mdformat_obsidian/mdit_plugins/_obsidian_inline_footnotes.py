"""Obsidian Inline Footnotes.

Docs: https://help.obsidian.md/Editing+and+formatting/Basic+formatting+syntax#Footnotes

"""

from __future__ import annotations

import re

from markdown_it import MarkdownIt
from markdown_it.rules_block import StateBlock
from mdit_py_plugins.utils import is_code_block

from mdformat_obsidian.factories import new_token

OBSIDIAN_INLINE_FOOTNOTE_PREFIX = "obsidian_inline_footnote"
"""Prefix used to differentiate the parsed output."""

_PATTERN = re.compile(r"^(?P<other>.+) \^\\?\[(?P<footnote>[^\]]+)\\?\]")
"""Regular expression to match inline footnotes."""


def _new_match(state: StateBlock, start_line: int) -> re.Match[str] | None:
    """Determine match between start and end lines."""
    start = state.bMarks[start_line] + state.tShift[start_line]
    maximum = state.eMarks[start_line]
    return _PATTERN.match(state.src[start:maximum])


def _inline_footnote(
    state: StateBlock,
    start_line: int,
    end_line: int,
    silent: bool,
) -> bool:
    """Identify inline footnotes."""
    if is_code_block(state, start_line):
        return False

    match = _new_match(state, start_line)
    if match is None:
        return False

    if silent:
        return True

    with new_token(state, OBSIDIAN_INLINE_FOOTNOTE_PREFIX, "p"):
        tkn_inline = state.push("inline", "", 0)
        tkn_inline.content = f'{match["other"]} ^[{match["footnote"]}]'
        tkn_inline.map = [start_line, end_line]
        tkn_inline.children = []

    state.line = end_line + 1

    return True


def obsidian_inline_footnote_plugin(md: MarkdownIt) -> None:
    md.block.ruler.before(
        "paragraph",
        OBSIDIAN_INLINE_FOOTNOTE_PREFIX,
        _inline_footnote,
        {"alt": ["paragraph"]},
    )
