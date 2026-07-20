"""Public Extension."""

from __future__ import annotations

import textwrap
from collections.abc import Mapping

from markdown_it import MarkdownIt
from mdformat.renderer import RenderContext, RenderTreeNode
from mdformat.renderer.typing import Render

from .mdit_plugins import (
    INLINE_SEP,
    OBSIDIAN_CALLOUT_PREFIX,
    footnote_plugin,
    format_footnote,
    format_footnote_block,
    format_footnote_ref,
    obsidian_callout_plugin,
    obsidian_dollarmath_plugin,
    tasklists_plugin,
)


def update_mdit(mdit: MarkdownIt) -> None:
    """Update the parser to identify Alerts."""
    mdit.use(obsidian_dollarmath_plugin)
    mdit.use(footnote_plugin)
    mdit.use(obsidian_callout_plugin)
    mdit.use(tasklists_plugin)


def _render_obsidian_callout(node: RenderTreeNode, context: RenderContext) -> str:
    """Render a `RenderTreeNode`."""
    title_line = node.markup.replace(INLINE_SEP, "")
    elements = [render for child in node.children if (render := child.render(context))]
    # Do not separate the title line from the first row
    return "\n".join([title_line, "\n\n".join(elements)]).rstrip()


def _no_render(
    node: RenderTreeNode,  # noqa: ARG001
    context: RenderContext,  # noqa: ARG001
) -> str:
    """Skip rendering when handled separately."""
    return ""


def _recursive_render(
    node: RenderTreeNode,
    context: RenderContext,
) -> str:
    elements = [render for child in node.children if (render := child.render(context))]
    # Do not separate the title line from the first row
    return "\n\n".join(elements).rstrip()


# ================================================================================
# Dollar Math. Adapted from mdformat-myst and mdformat-mkdocs:
# https://github.com/executablebooks/mdformat-myst/blob/e12a64c7e3f695ea7c3ba9b33abd79c219a01750/mdformat_myst/plugin.py#L53C1-L133
# https://github.com/KyleKing/mdformat-mkdocs/blob/main/mdformat_mkdocs/plugin.py
# ================================================================================


def _math_inline_renderer(node: RenderTreeNode, context: RenderContext) -> str:  # noqa: ARG001
    return f"${node.content}$"


def _strip_blockquote_markers(content: str) -> str:
    """Strip blockquote markers from math block content.

    markdown-it includes "> " prefixes when block math appears inside blockquotes.
    """
    lines = content.split("\n")
    return "\n".join(
        line.removeprefix("> ") if line.startswith("> ") else line for line in lines
    )


def _split_math_block_content(content: str) -> tuple[str, str, str]:
    """Split math block content into (cleaned content, leading sep, trailing sep).

    A separator is a newline if the raw content already had whitespace on that
    side (safe to normalize, since that whitespace collapses the same way
    whether it's a space or a newline), and empty otherwise. Content with no
    surrounding whitespace must not gain a separator: inserting one would
    change the math block's rendered text content, so the plugin's
    idempotency validation would fail.

    `node.content` retains the raw source indentation of continuation lines
    (e.g. list-item or blockquote indent). Dedenting it here, rather than
    leaving it embedded, prevents it from being re-applied by mdformat's
    list-item wrapper on every format pass, which would otherwise compound
    the indentation each pass.
    """
    unquoted = textwrap.dedent(_strip_blockquote_markers(content))
    leading_sep = "\n" if unquoted[:1].isspace() else ""
    trailing_sep = "\n" if unquoted[-1:].isspace() else ""
    return unquoted.strip(), leading_sep, trailing_sep


def _math_block_renderer(node: RenderTreeNode, context: RenderContext) -> str:  # noqa: ARG001
    cleaned_content, leading_sep, trailing_sep = _split_math_block_content(node.content)
    return f"$${leading_sep}{cleaned_content}{trailing_sep}$$"


def _math_block_label_renderer(node: RenderTreeNode, context: RenderContext) -> str:
    return f"{_math_block_renderer(node, context)} ({node.info})"


# ================================================================================
# End Dollar Math
# ================================================================================

# A mapping from syntax tree node type to a function that renders it.
# This can be used to overwrite renderer functions of existing syntax
# or add support for new syntax.
RENDERERS: Mapping[str, Render] = {
    "footnote": format_footnote,
    "footnote_block": format_footnote_block,
    "footnote_ref": format_footnote_ref,
    "math_block": _math_block_renderer,
    "math_block_label": _math_block_label_renderer,
    "math_inline": _math_inline_renderer,
    OBSIDIAN_CALLOUT_PREFIX: _render_obsidian_callout,
    f"{OBSIDIAN_CALLOUT_PREFIX}_title": _no_render,
    f"{OBSIDIAN_CALLOUT_PREFIX}_title_inner": _no_render,
    f"{OBSIDIAN_CALLOUT_PREFIX}_collapsed": _no_render,
    # NOTE: The content div uses recursive_render to properly handle nested content
    # without introducing extra newlines that would create unwanted block elements
    f"{OBSIDIAN_CALLOUT_PREFIX}_content": _recursive_render,
}
