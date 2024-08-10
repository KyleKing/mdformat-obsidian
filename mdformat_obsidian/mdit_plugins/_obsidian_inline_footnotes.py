"""Obsidian Inline Footnotes.

Docs: https://help.obsidian.md/Editing+and+formatting/Basic+formatting+syntax#Footnotes

"""

from __future__ import annotations

import re

from markdown_it import MarkdownIt
from markdown_it.rules_inline import StateInline

from mdformat_obsidian.factories import new_token

OBSIDIAN_INLINE_FOOTNOTE_PREFIX = "obsidian_inline_footnote"
"""Prefix used to differentiate the parsed output."""

_PATTERN = re.compile(r"(?<= )\^\\?\[(?P<footnote>[^\]]+)\\?\]")
"""Regular expression to match inline footnotes."""


def _inline_footnote(state: StateInline, silent: bool) -> bool:
    """Identify inline footnotes."""
    match = _PATTERN.search(state.src[state.pos : state.posMax])
    if not match:
        return False

    if silent:
        return True

    pos = state.pos
    state.pos = match.start()
    with new_token(state, OBSIDIAN_INLINE_FOOTNOTE_PREFIX, "a") as token:
        token.meta = {"content": f'^[{match["footnote"]}]'}

    state.pos = pos
    state.pos += match.end()

    return True


def obsidian_inline_footnote_plugin(md: MarkdownIt) -> None:
    md.inline.ruler.before(
        "text",
        OBSIDIAN_INLINE_FOOTNOTE_PREFIX,
        _inline_footnote,
        {"alt": ["text"]},
    )
