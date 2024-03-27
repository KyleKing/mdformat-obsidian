"""Public Extension."""

from __future__ import annotations

from typing import Mapping

from markdown_it import MarkdownIt
from mdformat.renderer import RenderContext, RenderTreeNode
from mdformat.renderer.typing import Render

from .mdit_plugins import INLINE_SEP, OBSIDIAN_CALLOUT_PREFIX, obsidian_callout_plugin


def update_mdit(mdit: MarkdownIt) -> None:
    """Update the parser to identify Alerts."""
    mdit.use(obsidian_callout_plugin)


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


# A mapping from syntax tree node type to a function that renders it.
# This can be used to overwrite renderer functions of existing syntax
# or add support for new syntax.
RENDERERS: Mapping[str, Render] = {
    OBSIDIAN_CALLOUT_PREFIX: _render_obsidian_callout,
    f"{OBSIDIAN_CALLOUT_PREFIX}_title": _no_render,
    f"{OBSIDIAN_CALLOUT_PREFIX}_title_inner": _no_render,
    f"{OBSIDIAN_CALLOUT_PREFIX}_collapsed": _no_render,
    # FIXME: can I add divs without introducing new blocks?
    f"{OBSIDIAN_CALLOUT_PREFIX}_content": _recursive_render,
}
