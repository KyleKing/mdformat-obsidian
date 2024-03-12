"""Obsidian Callouts."""

from __future__ import annotations

from markdown_it.rules_block import StateBlock

from ..factories import (
    CalloutData,
    new_token,
    obsidian_callout_plugin_factory,
    parse_possible_blockquote_admon_factory,
)

OBSIDIAN_CALLOUT_PREFIX = "obsidian_callout"
"""Prefix used to differentiate the parsed output."""

INLINE_SEP = "\n\n"
"""Optional separator to differentiate the title and ineline content (if present)."""

PATTERNS = {
    # Note '> ' prefix is removed when parsing
    r"^\*\*(?P<title>Note|Warning)\*\*",
    # FYI: Unlike GitHub Alerts, Obsidian doesn't constrain the possible types
    r"^\\?\[!(?P<title>[^\]]+)\\?\](?P<fold>-?)",
}
"""Patterns specific to GitHub Alerts."""


def format_obsidian_callout_markup(
    state: StateBlock,
    start_line: int,
    admonition: CalloutData,
) -> None:
    """Format markup."""
    title_line = (
        f"[!{admonition.meta_text.upper()}]{INLINE_SEP}{admonition.custom_title}"
    )

    with new_token(state, OBSIDIAN_CALLOUT_PREFIX, "div") as token:
        token.attrs = {
            "class": f"markdown-alert markdown-alert-{admonition.meta_text.lower()}",
        }
        token.block = True
        token.map = [start_line, admonition.next_line]
        token.markup = title_line
        with new_token(state, f"{OBSIDIAN_CALLOUT_PREFIX}_title", "p") as tkn_title:
            tkn_title.attrs = {"class": "markdown-alert-title"}

            tkn_title_txt = state.push("inline", "", 0)
            tkn_title_txt.content = admonition.meta_text.title()

        # FIXME: This is the title, not the extra content!
        if admonition.custom_title:
            with new_token(state, f"{OBSIDIAN_CALLOUT_PREFIX}_inline", "p"):
                tkn_inline_txt = state.push("inline", "", 0)
                tkn_inline_txt.content = admonition.custom_title.strip()

        state.md.block.tokenize(state, start_line + 1, admonition.next_line)

    # FIXME: this isn't actually replacing the block quote outer div?
    #
    # Render as a div for accessibility rather than block quote
    #   Which is because '>' is being misused (https://github.com/orgs/community/discussions/16925#discussioncomment-8729846)
    state.parentType = "div"  # admonition.old_state.parentType
    state.lineMax = admonition.old_state.lineMax
    state.line = admonition.next_line


def alert_logic(
    state: StateBlock,
    startLine: int,
    endLine: int,
    silent: bool,
) -> bool:
    """Parse GitHub Alerts."""
    parser_func = parse_possible_blockquote_admon_factory(
        OBSIDIAN_CALLOUT_PREFIX,
        PATTERNS,
    )
    result = parser_func(state, startLine, endLine, silent)
    if isinstance(result, CalloutData):
        format_obsidian_callout_markup(state, startLine, admonition=result)
        return True
    return result


obsidian_callout_plugin = obsidian_callout_plugin_factory(
    OBSIDIAN_CALLOUT_PREFIX,
    alert_logic,
)
