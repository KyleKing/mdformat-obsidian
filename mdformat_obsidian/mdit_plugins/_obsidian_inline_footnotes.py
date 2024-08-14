"""Obsidian Inline Footnotes.

Docs: https://help.obsidian.md/Editing+and+formatting/Basic+formatting+syntax#Footnotes

TODO: Add rendering support to mdformat-footnote:
https://github.com/executablebooks/mdformat-footnote/blob/80852fc20cfba7fd0330b9ac7a1a4df983542942/mdformat_footnote/plugin.py#L17

HACK: Under MIT license, code is adapted from:
https://github.com/executablebooks/mdformat-footnote/blob/80852fc20cfba7fd0330b9ac7a1a4df983542942/mdformat_footnote/plugin.py#L19C1-L51

"""

from __future__ import annotations

import textwrap
from contextlib import suppress

from mdformat.renderer import RenderContext, RenderTreeNode


def format_footnote(node: RenderTreeNode, context: RenderContext) -> str:
    """Extend footnote formatting to exclude inline."""
    if not node.meta["label"]:
        return ""

    first_line = f"[^{node.meta['label']}]:"
    indent = " " * 4
    elements = []
    with context.indented(len(indent)):
        for child in node.children:
            if child.type == "footnote_anchor":
                continue
            elements.append(child.render(context))
    body = textwrap.indent("\n\n".join(elements), indent)
    # if the first body element is a paragraph, we can start on the first line,
    # otherwise we start on the second line
    if body and node.children and node.children[0].type != "paragraph":
        body = "\n" + body
    else:
        body = " " + body.lstrip()
    return first_line + body


def format_footnote_ref(node: RenderTreeNode, context: RenderContext) -> str:
    """Extend footnote refs to support inline footnote formatting."""
    with suppress(KeyError):
        return f"[^{node.meta['label']}]"
    # Locate footnote content by id
    content = context.env["footnotes"]["list"][node.meta["id"]]["content"]
    return f"^[{content}]"


def format_footnote_block(node: RenderTreeNode, context: RenderContext) -> str:
    return "\n\n".join(child.render(context) for child in node.children)
