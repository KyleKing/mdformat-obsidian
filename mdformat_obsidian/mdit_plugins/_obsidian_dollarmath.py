"""Guard around `dollarmath_plugin`'s block rule for an ambiguous same-line case.

`mdit_py_plugins.dollarmath`'s block rule only recognizes a same-line close
(``$$content$$``) when the closing ``$$`` is the last thing on the line. If
trailing text follows it (e.g. ``$$b$$ Binomial``), that check fails and the
rule instead scans forward for the *next* ``$$`` anywhere in the document,
silently swallowing everything in between (including subsequent list items)
as literal math content. Each re-format pass then re-embeds the swallowed
lines' indentation, growing it without bound.

Rather than trying to correctly parse the ambiguous line (splitting a single
source line between a closed math span and trailing paragraph text isn't
supported by markdown-it's line-based block model without deeper surgery),
this rejects the match entirely for that line. The line then falls through
to normal paragraph/inline handling, which is stable and matches how the
line would render without dollarmath enabled at all.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from markdown_it import MarkdownIt
from mdit_py_plugins.dollarmath import dollarmath_plugin

if TYPE_CHECKING:
    from collections.abc import Callable

    from markdown_it.rules_block import StateBlock

    _BlockRuleFn = Callable[[StateBlock, int, int, bool], bool]


def _is_ambiguous_same_line_close(state: StateBlock, start_line: int) -> bool:
    """True if the line opens `$$`, closes it, then has trailing content.

    e.g. `$$b$$ Binomial`: a legitimate close exists, but it isn't the last
    thing on the line, which is the one case the underlying block rule
    doesn't handle safely.
    """
    pos = state.bMarks[start_line] + state.tShift[start_line]
    end = state.eMarks[start_line]
    stripped = state.src[pos:end].strip()
    return (
        stripped.startswith("$$")
        and "$$" in stripped[2:]
        and not stripped.endswith("$$")
    )


def obsidian_dollarmath_plugin(md: MarkdownIt) -> None:
    """Register `dollarmath_plugin`, guarded against the same-line-close bug."""
    md.use(dollarmath_plugin)
    for rule in md.block.ruler.__rules__:
        if rule.name == "math_block":
            original_fn: _BlockRuleFn = rule.fn

            def guarded(
                state: StateBlock,
                start_line: int,
                end_line: int,
                silent: bool,
                _original_fn: _BlockRuleFn = original_fn,
            ) -> bool:
                if _is_ambiguous_same_line_close(state, start_line):
                    return False
                return _original_fn(state, start_line, end_line, silent)

            rule.fn = guarded
