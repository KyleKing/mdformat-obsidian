"""Obsidian Callouts."""

from __future__ import annotations

from typing import TYPE_CHECKING

from markdown_it import MarkdownIt
from markdown_it.rules_block import StateBlock

from mdformat_obsidian.factories import (
    CalloutData,
    new_token,
    parse_possible_blockquote_admon_factory,
)

if TYPE_CHECKING:
    from collections.abc import Sequence

    from markdown_it.renderer import RendererHTML
    from markdown_it.token import Token
    from markdown_it.utils import EnvType, OptionsDict

OBSIDIAN_CALLOUT_PREFIX = "obsidian_callout"
"""Prefix used to differentiate the parsed output."""

INLINE_SEP = "\n\n"
"""Optional separator to differentiate the title and, if present, inline content."""

PATTERN = r"^\\?\[!(?P<title>[^\]]+)\\?\](?P<fold>[\-\+]?)"
"""Regular expression to match Obsidian Alerts."""


def format_obsidian_callout_markup(
    state: StateBlock,
    start_line: int,
    admonition: CalloutData,
) -> None:
    """Format markup."""
    tag = admonition.meta_text.upper()
    folded = bool(admonition.fold)
    custom_title = admonition.custom_title
    title_line = f"[!{tag}]{admonition.fold}{INLINE_SEP}{custom_title}"

    with new_token(state, OBSIDIAN_CALLOUT_PREFIX, "div") as token:
        token.attrs = {
            "data-callout-metadata": "",
            "data-callout-fold": "",
            "data-callout": admonition.meta_text.lower(),
            "class": "callout",
        }
        if folded:
            token.attrs["data-callout-fold"] = "-"
            token.attrs["class"] = "callout is-collapsible is-collapsed"
        token.block = True
        token.map = [start_line, admonition.next_line]
        token.markup = title_line
        with new_token(state, f"{OBSIDIAN_CALLOUT_PREFIX}_title", "div") as tkn_title:
            tkn_title.attrs = {"class": "callout-title"}

            title_inner = f"{OBSIDIAN_CALLOUT_PREFIX}_title_inner"
            with new_token(state, title_inner, "div") as tkn_title_inner:
                tkn_title_inner.attrs = {"class": "callout-title-inner"}

                tkn_title_txt = state.push("inline", "", 0)
                tkn_title_txt.content = admonition.custom_title.strip()
            if folded:
                collapsed = f"{OBSIDIAN_CALLOUT_PREFIX}_collapsed"
                with new_token(state, collapsed, "div") as tkn_collapsed:
                    tkn_collapsed.attrs = {"class": "callout-fold is-collapsed"}

        content = f"{OBSIDIAN_CALLOUT_PREFIX}_content"
        with new_token(state, content, "div") as tkn_content:
            tkn_content.attrs = {"class": "callout-content"}
            if folded:
                tkn_content.attrs["style"] = "display: none;"

            state.md.block.tokenize(state, start_line + 1, admonition.next_line)

    # NOTE: The blockquote wrapper is rendered as a div in HTML output (see HTML renderers).
    # This improves accessibility since the '>' syntax is being repurposed for callouts.
    # The markdown tokens remain as blockquote to preserve mdformat compatibility.
    # Reference: https://github.com/orgs/community/discussions/16925#discussioncomment-8729846
    state.parentType = "div"  # admonition.old_state.parentType
    state.lineMax = admonition.old_state.lineMax
    state.line = admonition.next_line


def alert_logic(
    state: StateBlock,
    startLine: int,
    endLine: int,
    silent: bool,
) -> bool:
    """Parse Obsidian Alerts."""
    parser_func = parse_possible_blockquote_admon_factory(
        OBSIDIAN_CALLOUT_PREFIX,
        {PATTERN},
    )
    result = parser_func(state, startLine, endLine, silent)
    if isinstance(result, CalloutData):
        format_obsidian_callout_markup(state, startLine, admonition=result)
        return True
    return result


def _render_callout_open(
    self: RendererHTML,
    tokens: Sequence[Token],
    idx: int,
    _options: OptionsDict,
    _env: EnvType,
) -> str:
    """Render opening tag for callout elements."""
    token = tokens[idx]
    # Build attributes string using the renderer's renderAttrs method
    attrs_str = self.renderAttrs(token)
    # Check if next token is inline or a closing tag to avoid extra newlines
    if idx + 1 < len(tokens):
        next_token = tokens[idx + 1]
        # Don't add newline if next is inline content or immediately closing
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


def _render_blockquote_with_callout(
    self: RendererHTML,
    tokens: Sequence[Token],
    idx: int,
    options: OptionsDict,
    env: EnvType,
) -> str:
    """Render blockquote as div when it contains a callout for accessibility."""
    # Check if next token is an obsidian callout
    if (
        idx + 1 < len(tokens)
        and tokens[idx + 1].type == f"{OBSIDIAN_CALLOUT_PREFIX}_open"
    ):
        # Use div instead of blockquote for accessibility
        return "<div>\n"
    # Otherwise use default blockquote rendering
    return self.renderToken(tokens, idx, options, env)


def _render_blockquote_close_with_callout(
    self: RendererHTML,
    tokens: Sequence[Token],
    idx: int,
    options: OptionsDict,
    env: EnvType,
) -> str:
    """Close div when blockquote contained a callout."""
    # Look backwards to see if this closes a callout-containing blockquote
    # Find matching blockquote_open
    level = 1
    j = idx - 1
    while j >= 0 and level > 0:
        if tokens[j].type == "blockquote_close":
            level += 1
        elif tokens[j].type == "blockquote_open":
            level -= 1
            if level == 0:
                # Check if callout follows the opening blockquote
                if (
                    j + 1 < len(tokens)
                    and tokens[j + 1].type == f"{OBSIDIAN_CALLOUT_PREFIX}_open"
                ):
                    return "</div>\n"
                break
        j -= 1
    # Otherwise use default blockquote rendering
    return self.renderToken(tokens, idx, options, env)


def obsidian_callout_plugin(md: MarkdownIt) -> None:
    """Install the obsidian callout plugin."""
    md.block.ruler.before("blockquote", OBSIDIAN_CALLOUT_PREFIX, alert_logic)

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
        f"{OBSIDIAN_CALLOUT_PREFIX}_title_inner_open", _render_callout_open, fmt="html"
    )
    md.add_render_rule(
        f"{OBSIDIAN_CALLOUT_PREFIX}_title_inner_close",
        _render_callout_close,
        fmt="html",
    )
    md.add_render_rule(
        f"{OBSIDIAN_CALLOUT_PREFIX}_collapsed_open", _render_callout_open, fmt="html"
    )
    md.add_render_rule(
        f"{OBSIDIAN_CALLOUT_PREFIX}_collapsed_close", _render_callout_close, fmt="html"
    )
    md.add_render_rule(
        f"{OBSIDIAN_CALLOUT_PREFIX}_content_open", _render_callout_open, fmt="html"
    )
    md.add_render_rule(
        f"{OBSIDIAN_CALLOUT_PREFIX}_content_close", _render_callout_close, fmt="html"
    )

    # Override blockquote rendering to use div for callouts (accessibility)
    md.add_render_rule("blockquote_open", _render_blockquote_with_callout, fmt="html")
    md.add_render_rule(
        "blockquote_close", _render_blockquote_close_with_callout, fmt="html"
    )
