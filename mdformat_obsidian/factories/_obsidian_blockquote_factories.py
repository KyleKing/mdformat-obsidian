"""Logic Factories.

Adapted from the implementation for `mdformat-gfm-alerts`:
<https://github.com/KyleKing/mdformat-gfm-alerts/blob/a6e71db4da3a421320e75b8a9e3e3cb2dca429d7/mdformat_gfm_alerts/factories/_gfm_blockquote_factories.py>

"""

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


# FYI: copied from mdformat_admon.factories
@contextmanager
def new_token(state: StateBlock, name: str, kind: str) -> Generator[Token, None, None]:
    """Creates scoped token."""
    yield state.push(f"{name}_open", kind, 1)
    state.push(f"{name}_close", kind, -1)


# FYI: Adapted from mdformat_admon.factories
class CalloutState(NamedTuple):
    """Frozen state."""

    parentType: str
    lineMax: int


class CalloutData(NamedTuple):
    """CalloutData data for rendering."""

    old_state: CalloutState
    meta_text: str
    folded: bool
    custom_title: str
    next_line: int


def parse_possible_blockquote_admon_factory(
    prefix: str,
    patterns: set[str],
) -> Callable[[StateBlock, int, int, bool], CalloutData | bool]:
    """Generate the parser function.

    Accepts set of strings that will be compiled into regular expressions.
    They must have a capture group `title` and optional group `folded`.

    """

    def parse_possible_blockquote_admon(
        state: StateBlock,
        start_line: int,
        end_line: int,
        silent: bool,
    ) -> CalloutData | bool:
        if is_code_block(state, start_line):
            return False

        start = state.bMarks[start_line] + state.tShift[start_line]

        # Exit if no match for any pattern
        text = state.src[start:]
        regexes = [
            re.compile(rf"{pat}(?P<custom_title>(?: |<br>)[^\n]+)?", re.IGNORECASE)
            for pat in patterns
        ]
        match = next((_m for rx in regexes if (_m := rx.match(text))), None)
        if not match:
            return False

        # Since start is found, we can report success here in validation mode
        if silent:
            return True

        old_state = CalloutState(
            parentType=state.parentType,
            lineMax=state.lineMax,
        )
        state.parentType = prefix

        return CalloutData(
            old_state=old_state,
            meta_text=match["title"],
            folded=bool(match["folded"]),
            custom_title=match["custom_title"] or "",
            next_line=end_line,
        )

    return parse_possible_blockquote_admon


def obsidian_callout_plugin_factory(
    prefix: str,
    logic: Callable[[StateBlock, int, int, bool], bool],
) -> Callable[[MarkdownIt], None]:
    """Generate the plugin function."""

    def obsidian_callout_plugin(md: MarkdownIt) -> None:
        md.block.ruler.before("blockquote", prefix, logic)

    return obsidian_callout_plugin
