"""Generic Alert/Callout Factories.

This module provides reusable factories for converting blockquotes containing
special syntax (like alerts, callouts, admonitions) into custom tokens.

Adapted from implementations in:
- mdformat-gfm-alerts: <https://github.com/KyleKing/mdformat-gfm-alerts>
- mdformat-obsidian: <https://github.com/KyleKing/mdformat-obsidian>

"""

from __future__ import annotations

import re
from collections.abc import Callable, Sequence
from dataclasses import dataclass
from typing import TYPE_CHECKING

from markdown_it import MarkdownIt
from markdown_it.rules_core import StateCore
from markdown_it.token import Token

if TYPE_CHECKING:
    from markdown_it.renderer import RendererHTML
    from markdown_it.utils import EnvType, OptionsDict


@dataclass
class AlertMatch:
    """Information about a matched alert/callout in a blockquote."""

    title: str
    marker: str
    inline_content: str
    full_match: re.Match[str]


def _get_first_inline(tokens: list[Token], start: int, end: int) -> Token | None:
    """Get the first inline token in a range."""
    return next(
        (t for t in tokens[start : end + 1] if t.type == "inline"),
        None,
    )


def blockquote_to_alert_factory(
    prefix: str,  # noqa: ARG001
    patterns: Sequence[re.Pattern[str]],
    transform_callback: Callable[[list[Token], int, int, AlertMatch], None],
    *,
    parse_nested: bool = True,
) -> Callable[[StateCore], None]:
    """Create a core rule that transforms blockquotes to alerts.

    This factory creates a markdown-it core rule that:
    1. Scans through parsed tokens looking for blockquotes
    2. Checks if blockquote content matches any provided patterns
    3. Calls transform_callback to customize the token transformation

    Args:
        prefix: Token type prefix (e.g., "gfm_alert", "obsidian_callout")
        patterns: Regex patterns to match alert syntax (must have 'title' and 'marker' groups)
        transform_callback: Function to transform matched blockquote tokens
        parse_nested: Whether to parse nested blockquotes

    Returns:
        A core rule function that can be registered with markdown-it

    """

    def _try_match_alert(
        tokens: list[Token], start_index: int, end_index: int
    ) -> AlertMatch | None:
        """Try to match alert syntax in blockquote."""
        first_inline = _get_first_inline(tokens, start_index, end_index)
        if not first_inline:
            return None

        for pattern in patterns:
            if match := pattern.match(first_inline.content):
                return AlertMatch(
                    title=match.group("title").strip(),
                    marker=match.group("marker"),
                    inline_content=match.group("inline")
                    if "inline" in match.groupdict()
                    else "",
                    full_match=match,
                )
        return None

    def core_rule(state: StateCore) -> None:
        """Core rule that transforms blockquotes to alerts."""
        tokens = state.tokens
        i = 0
        start_indices = []
        while i < len(tokens):
            if tokens[i].type == "blockquote_open":
                start_indices.append(i)
            elif tokens[i].type == "blockquote_close":
                start_index = start_indices.pop()
                if (parse_nested or not start_indices) and (
                    alert_match := _try_match_alert(tokens, start_index, i)
                ):
                    transform_callback(tokens, start_index, i, alert_match)
            i += 1

    return core_rule


def blockquote_to_div_plugin_factory(
    alert_prefix: str,
) -> Callable[[MarkdownIt], None]:
    """Create a plugin that converts blockquotes containing alerts to divs.

    This improves accessibility when blockquotes are repurposed for semantic
    content (like callouts, alerts, admonitions) rather than actual quotations.

    The blockquote tokens remain in the AST for mdformat compatibility, but are
    rendered as <div> elements in HTML when they contain the specified alert type.

    Args:
        alert_prefix: The token type prefix to detect (e.g., "gfm_alert", "obsidian_callout")

    Returns:
        A plugin function that can be applied to a MarkdownIt instance

    """

    def _render_blockquote_open_with_alert(
        self: RendererHTML,
        tokens: Sequence[Token],
        idx: int,
        options: OptionsDict,
        env: EnvType,
    ) -> str:
        """Render blockquote as div when it contains an alert for accessibility."""
        if idx + 1 < len(tokens) and tokens[idx + 1].type == f"{alert_prefix}_open":
            return "<div>\n"
        return self.renderToken(tokens, idx, options, env)

    def _render_blockquote_close_with_alert(
        self: RendererHTML,
        tokens: Sequence[Token],
        idx: int,
        options: OptionsDict,
        env: EnvType,
    ) -> str:
        """Close div when blockquote contained an alert."""
        level = 1
        j = idx - 1
        while j >= 0 and level > 0:
            if tokens[j].type == "blockquote_close":
                level += 1
            elif tokens[j].type == "blockquote_open":
                level -= 1
                if level == 0:
                    if (
                        j + 1 < len(tokens)
                        and tokens[j + 1].type == f"{alert_prefix}_open"
                    ):
                        return "</div>\n"
                    break
            j -= 1
        return self.renderToken(tokens, idx, options, env)

    def blockquote_to_div_plugin(md: MarkdownIt) -> None:
        """Install the blockquote-to-div conversion plugin."""
        md.add_render_rule(
            "blockquote_open", _render_blockquote_open_with_alert, fmt="html"
        )
        md.add_render_rule(
            "blockquote_close", _render_blockquote_close_with_alert, fmt="html"
        )

    return blockquote_to_div_plugin
