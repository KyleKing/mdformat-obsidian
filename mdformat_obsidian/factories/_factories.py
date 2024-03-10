"""GitHub Alerts."""

from __future__ import annotations

import re
from collections.abc import Generator
from contextlib import contextmanager
from typing import TYPE_CHECKING, Callable, NamedTuple

from markdown_it import MarkdownIt
from markdown_it.rules_block import StateBlock
from mdit_py_plugins.utils import is_code_block

if TYPE_CHECKING:
    from markdown_it.token import Token

PREFIX = "gfm_alert"
"""Prefix used to differentiate the parsed output."""


# FYI: copied from mdformat_admon.factories
@contextmanager
def new_token(state: StateBlock, name: str, kind: str) -> Generator[Token, None, None]:
    """Creates scoped token."""
    yield state.push(f"{name}_open", kind, 1)
    state.push(f"{name}_close", kind, -1)


# FYI: Adapted from mdformat_admon.factories._factories
class AlertState(NamedTuple):
    """Frozen state."""

    parentType: str
    lineMax: int


class AlertData(NamedTuple):
    """AlertData data for rendering."""

    old_state: AlertState
    meta_text: str
    inline_content: str
    next_line: int


def parse_possible_blockquote_admon_factory(
    patterns: set[str],
) -> Callable[[StateBlock, int, int, bool], AlertData | bool]:
    """Generate the parser function.

    Accepts set of strings that will be compiled into regular expressions.
    They must have a capture group `title`.

    """

    def parse_possible_blockquote_admon(
        state: StateBlock,
        start_line: int,
        end_line: int,
        silent: bool,
    ) -> AlertData | bool:
        if is_code_block(state, start_line):
            return False

        start = state.bMarks[start_line] + state.tShift[start_line]

        # Exit if no match for any pattern
        text = state.src[start:]
        regexes = [
            re.compile(rf"{pat}(?P<inline_content>(?: |<br>)[^\n]+)?", re.IGNORECASE)
            for pat in patterns
        ]
        match = next((_m for rx in regexes if (_m := rx.match(text))), None)
        if not match:
            return False

        # Since start is found, we can report success here in validation mode
        if silent:
            return True

        old_state = AlertState(
            parentType=state.parentType,
            lineMax=state.lineMax,
        )
        state.parentType = "gfm_alert"

        return AlertData(
            old_state=old_state,
            meta_text=match["title"],
            inline_content=match["inline_content"] or "",
            next_line=end_line,
        )

    return parse_possible_blockquote_admon


def gfm_alert_plugin_factory(
    prefix: str,
    logic: Callable[[StateBlock, int, int, bool], bool],
) -> Callable[[MarkdownIt], None]:
    """Generate the plugin function."""

    def gfm_alert_plugin(md: MarkdownIt) -> None:
        md.block.ruler.before("blockquote", prefix, logic)

    return gfm_alert_plugin
