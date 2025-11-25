"""Obsidian Callouts."""

from __future__ import annotations

import re
from typing import TYPE_CHECKING

from markdown_it import MarkdownIt
from markdown_it.token import Token

from mdformat_obsidian._synced.alert_factories import (
    AlertMatch,
    blockquote_to_alert_factory,
    blockquote_to_div_plugin_factory,
)

if TYPE_CHECKING:
    from collections.abc import Sequence

    from markdown_it.renderer import RendererHTML
    from markdown_it.utils import EnvType, OptionsDict

OBSIDIAN_CALLOUT_PREFIX = "obsidian_callout"
"""Prefix used to differentiate the parsed output."""

INLINE_SEP = "\n\n"
"""Optional separator to differentiate the title and, if present, inline content."""

PATTERN = re.compile(
    r"^(?P<marker>\\?\[!(?P<title>[^\]]+)\\?\])(?P<fold>[\-\+]?)[ \t]*(?P<inline>[^\n\r]*)?",
    re.IGNORECASE,
)
"""Regular expression to match Obsidian Callouts."""


def _render_callout_open(
    self: RendererHTML,
    tokens: Sequence[Token],
    idx: int,
    _options: OptionsDict,
    _env: EnvType,
) -> str:
    """Render opening tag for callout elements."""
    token = tokens[idx]
    attrs_str = self.renderAttrs(token)
    if idx + 1 < len(tokens):
        next_token = tokens[idx + 1]
        next_is_inline_or_close = (
            next_token.type == "inline" or next_token.nesting == -1
        )
        newline = "" if next_is_inline_or_close else "\n"
    else:
        newline = "\n"
    return f"<{token.tag}{attrs_str}>{newline}"


def _render_callout_close(
    _self: RendererHTML,
    tokens: Sequence[Token],
    idx: int,
    _options: OptionsDict,
    _env: EnvType,
) -> str:
    """Render closing tag for callout elements."""
    return f"</{tokens[idx].tag}>\n"


def obsidian_callout_plugin(md: MarkdownIt) -> None:
    """Install the obsidian callout plugin."""

    def _transform_to_callout(
        tokens: list[Token],
        start_index: int,
        end_index: int,
        alert_match: AlertMatch,
    ) -> None:
        """Transform blockquote tokens to Obsidian callout tokens."""
        # Get first inline token to check if we need to strip the callout marker from it
        first_inline = next(
            (t for t in tokens[start_index : end_index + 1] if t.type == "inline"),
            None,
        )

        # Extract fold status from the match
        fold = alert_match.full_match.group("fold") if "fold" in alert_match.full_match.groupdict() else ""
        folded = bool(fold)

        # Get custom title from inline content (text on the same line as the marker)
        custom_title = alert_match.inline_content.strip()

        # If there's a custom title on the same line, we need to remove it from the first inline token
        # Otherwise, the first inline token contains the actual content
        if first_inline and custom_title:
            # The first inline contains: marker + fold + custom_title + newline + actual content
            # We need to strip the marker + fold + custom_title part
            marker_with_fold = alert_match.marker
            if fold:
                marker_with_fold += fold
            if custom_title:
                marker_with_fold += " " + custom_title
            # Remove the full marker line from the content
            content = first_inline.content
            if content.startswith(marker_with_fold):
                first_inline.content = content[len(marker_with_fold):].lstrip()
        elif first_inline:
            # No custom title, just remove the marker and fold from content
            marker_with_fold = alert_match.marker
            if fold:
                marker_with_fold += fold
            content = first_inline.content
            if content.startswith(marker_with_fold):
                first_inline.content = content[len(marker_with_fold):].lstrip()

        # Transform open token
        open_token = tokens[start_index]
        open_token.type = f"{OBSIDIAN_CALLOUT_PREFIX}_open"
        open_token.tag = "div"
        open_token.attrs = {
            "data-callout-metadata": "",
            "data-callout-fold": "",
            "data-callout": alert_match.title.lower(),
            "class": "callout",
        }
        # Store custom title in attrs for rendering
        if custom_title:
            open_token.attrs["data-callout-title"] = custom_title

        if folded:
            open_token.attrs["data-callout-fold"] = fold
            open_token.attrs["class"] = "callout is-collapsible is-collapsed"

        # Transform close token
        close_token = tokens[end_index]
        close_token.type = f"{OBSIDIAN_CALLOUT_PREFIX}_close"
        close_token.tag = "div"

        # Insert title token after the open token
        # The title will be rendered from attrs
        title_token = Token(f"{OBSIDIAN_CALLOUT_PREFIX}_title_open", "p", 1)
        title_token.attrs = {"class": "callout-title"}
        title_token.block = True

        title_inline = Token("inline", "", 0)
        title_inline.content = custom_title or alert_match.title.title()
        title_inline.children = []

        title_close = Token(f"{OBSIDIAN_CALLOUT_PREFIX}_title_close", "p", -1)

        # Insert these tokens right after the open token
        insert_pos = start_index + 1
        tokens.insert(insert_pos, title_token)
        tokens.insert(insert_pos + 1, title_inline)
        tokens.insert(insert_pos + 2, title_close)

        # If folded, add fold indicator tokens
        if folded:
            fold_open = Token(f"{OBSIDIAN_CALLOUT_PREFIX}_fold_open", "div", 1)
            fold_open.attrs = {"class": "callout-fold is-collapsed"}
            fold_close = Token(f"{OBSIDIAN_CALLOUT_PREFIX}_fold_close", "div", -1)
            tokens.insert(insert_pos + 3, fold_open)
            tokens.insert(insert_pos + 4, fold_close)

    # Create and register the core rule using the generic factory
    core_rule = blockquote_to_alert_factory(
        OBSIDIAN_CALLOUT_PREFIX,
        [PATTERN],
        _transform_to_callout,
        parse_nested=True,
    )
    md.core.ruler.after("block", OBSIDIAN_CALLOUT_PREFIX, core_rule)

    # Register renderers for all callout token types (only for HTML output)
    md.add_render_rule(
        f"{OBSIDIAN_CALLOUT_PREFIX}_open", _render_callout_open, fmt="html"
    )
    md.add_render_rule(
        f"{OBSIDIAN_CALLOUT_PREFIX}_close", _render_callout_close, fmt="html"
    )
    md.add_render_rule(
        f"{OBSIDIAN_CALLOUT_PREFIX}_title_open", _render_callout_open, fmt="html"
    )
    md.add_render_rule(
        f"{OBSIDIAN_CALLOUT_PREFIX}_title_close", _render_callout_close, fmt="html"
    )
    md.add_render_rule(
        f"{OBSIDIAN_CALLOUT_PREFIX}_fold_open", _render_callout_open, fmt="html"
    )
    md.add_render_rule(
        f"{OBSIDIAN_CALLOUT_PREFIX}_fold_close", _render_callout_close, fmt="html"
    )

    # Add blockquote-to-div conversion for accessibility
    blockquote_to_div_plugin = blockquote_to_div_plugin_factory(OBSIDIAN_CALLOUT_PREFIX)
    blockquote_to_div_plugin(md)
