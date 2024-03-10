"""Public Extension."""

from __future__ import annotations

from typing import Mapping

from markdown_it import MarkdownIt
from mdformat.renderer import RenderContext, RenderTreeNode
from mdformat.renderer.typing import Render

from .mdit_plugins import GFM_ALERT_PREFIX, INLINE_SEP, gfm_alert_plugin


def update_mdit(mdit: MarkdownIt) -> None:
    """Update the parser to identify Alerts."""
    mdit.use(gfm_alert_plugin)


def _render_gfm_alert(node: RenderTreeNode, context: RenderContext) -> str:
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


# A mapping from syntax tree node type to a function that renders it.
# This can be used to overwrite renderer functions of existing syntax
# or add support for new syntax.
RENDERERS: Mapping[str, Render] = {
    GFM_ALERT_PREFIX: _render_gfm_alert,
    f"{GFM_ALERT_PREFIX}_title": _no_render,
    f"{GFM_ALERT_PREFIX}_inline": _no_render,
}
