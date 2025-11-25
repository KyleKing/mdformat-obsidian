"""Public Extension."""

from __future__ import annotations

from collections.abc import Mapping

from markdown_it import MarkdownIt
from mdformat.renderer import RenderContext, RenderTreeNode
from mdformat.renderer.typing import Render
from mdit_py_plugins.dollarmath import dollarmath_plugin

from .mdit_plugins import (
    OBSIDIAN_CALLOUT_PREFIX,
    footnote_plugin,
    format_footnote,
    format_footnote_block,
    format_footnote_ref,
    obsidian_callout_plugin,
    tasklists_plugin,
)


def update_mdit(mdit: MarkdownIt) -> None:
    """Update the parser to identify Alerts."""
    mdit.use(dollarmath_plugin)
    mdit.use(footnote_plugin)
    mdit.use(obsidian_callout_plugin)
    mdit.use(tasklists_plugin)


def _render_obsidian_callout(node: RenderTreeNode, context: RenderContext) -> str:
    """Render a callout `RenderTreeNode`."""
    if node.nester_tokens is not None:
        open_token = node.nester_tokens.opening

        # Extract title and fold from attrs
        title = str(open_token.attrs.get("data-callout", "note"))
        fold_attr = open_token.attrs.get("data-callout-fold", "")
        fold_marker = str(fold_attr) if fold_attr else ""
        custom_title_attr = open_token.attrs.get("data-callout-title", "")
        custom_title = str(custom_title_attr) if custom_title_attr else ""

        # Build the first line with marker and optional custom title
        if custom_title:
            marker_line = f"> [!{title.upper()}]{fold_marker} {custom_title}"
        else:
            marker_line = f"> [!{title.upper()}]{fold_marker}"

        # Collect content from children, skipping title and fold nodes and their descendants
        content_lines = []
        skip_until_close = None

        for child in node.children:
            # If we're skipping, check if this is the close token
            if skip_until_close:
                if child.type == skip_until_close:
                    skip_until_close = None
                continue

            # Check if this is a title or fold open token
            if child.type == f"{OBSIDIAN_CALLOUT_PREFIX}_title_open":
                skip_until_close = f"{OBSIDIAN_CALLOUT_PREFIX}_title_close"
                continue
            if child.type == f"{OBSIDIAN_CALLOUT_PREFIX}_fold_open":
                skip_until_close = f"{OBSIDIAN_CALLOUT_PREFIX}_fold_close"
                continue
            # Also skip standalone title/fold nodes
            if child.type in (
                f"{OBSIDIAN_CALLOUT_PREFIX}_title",
                f"{OBSIDIAN_CALLOUT_PREFIX}_fold",
            ):
                continue

            # Render this child
            rendered = child.render(context=context).strip()
            if rendered:
                # Filter out any lines that are ONLY callout markers (no content after the marker)
                # This handles edge cases where markers weren't properly removed during parsing
                filtered_lines = []
                for line in rendered.split("\n"):
                    # Check if this line is just a marker with no content
                    stripped = line.lstrip("> ").strip()
                    # Pattern for marker-only line: [!type] or [!type]- or [!type]+ with nothing after
                    is_marker_only = (
                        stripped.startswith("[!")
                        and "]" in stripped
                        and stripped.split("]", 1)[1].strip() in ("", "-", "+")
                    )
                    if not is_marker_only:
                        filtered_lines.append(line)
                if filtered_lines:
                    content_lines.append("\n".join(filtered_lines))

        # Build result
        if content_lines:
            # Prefix each line with "> "
            result_parts = [marker_line]
            for content in content_lines:
                for line in content.split("\n"):
                    result_parts.append(f"> {line}")
            return "\n".join(result_parts) + "\n"

        return marker_line + "\n"
    raise ValueError("Callout node should have nester tokens.")


def _no_render(
    node: RenderTreeNode,  # noqa: ARG001
    context: RenderContext,  # noqa: ARG001
) -> str:
    """Skip rendering when handled separately."""
    return ""


# ================================================================================
# Dollar Math. Adapted from mdformat-myst:
# https://github.com/executablebooks/mdformat-myst/blob/e12a64c7e3f695ea7c3ba9b33abd79c219a01750/mdformat_myst/plugin.py#L53C1-L133
# ================================================================================


def _math_inline_renderer(node: RenderTreeNode, context: RenderContext) -> str:  # noqa: ARG001
    return f"${node.content}$"


def _math_block_renderer(node: RenderTreeNode, context: RenderContext) -> str:  # noqa: ARG001
    return f"$${node.content}$$"


def _math_block_label_renderer(node: RenderTreeNode, context: RenderContext) -> str:  # noqa: ARG001
    return f"$${node.content}$$ ({node.info})"


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
    f"{OBSIDIAN_CALLOUT_PREFIX}_title_open": _no_render,
    f"{OBSIDIAN_CALLOUT_PREFIX}_title_close": _no_render,
    f"{OBSIDIAN_CALLOUT_PREFIX}_fold": _no_render,
    f"{OBSIDIAN_CALLOUT_PREFIX}_fold_open": _no_render,
    f"{OBSIDIAN_CALLOUT_PREFIX}_fold_close": _no_render,
}
