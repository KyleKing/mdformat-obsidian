"""Obsidian Task Lists.

Loosely based on:
https://github.com/executablebooks/mdit-py-plugins/blob/d11bdaf0979e6fae01c35db5a4d1f6a4b4dd8843/mdit_py_plugins/tasklists/__init__.py

Extended to supports any mark character.

"""

from __future__ import annotations

import re

from markdown_it import MarkdownIt
from markdown_it.rules_core import StateCore
from markdown_it.token import Token

# Regex string to match a whitespace character, as specified in
# https://github.github.com/gfm/#whitespace-character
# (spec version 0.29-gfm (2019-04-06))
_GFM_WHITESPACE_RE = r"[ \t\n\v\f\r]"

_RE_TODO = re.compile(rf"\\?\[(?P<mark>.)\\?\]{_GFM_WHITESPACE_RE}+")


def tasklists_plugin(md: MarkdownIt) -> None:
    """Task List Plugin."""

    def todo_mark(tokens: list[Token], index: int) -> re.Match[str] | None:
        token = tokens[index]
        if (
            token.type == "inline"
            and tokens[index - 1].type == "paragraph_open"
            and tokens[index - 2].type == "list_item_open"
        ):
            # leading whitespace is already stripped by markdown-it
            return _RE_TODO.match(token.content)
        return None

    def todoify(match: re.Match[str], token: Token) -> None:
        checkbox = Token("html_inline", "", 0)
        mark = match["mark"].strip()
        checkbox.content = f"[{mark or ' '}] "

        assert token.children is not None  # for mypy
        # Remove escaped brackets
        # Addresses when children are: \[, <mark>, \], <content>, ...
        three = 3
        if len(token.children) > three and token.children[three - 1].content == "]":
            token.children = token.children[three:]
            token.children[0].content = token.children[0].content.lstrip()
            token.content = token.content.lstrip()
        else:
            start = match.end()
            token.children[0].content = token.children[0].content[start:]
            token.content = token.content[start:]
        token.children.insert(0, checkbox)

    def fcn(state: StateCore) -> None:
        tokens = state.tokens
        for idx in range(2, len(tokens) - 1):
            match = todo_mark(tokens, idx)
            if match:
                todoify(match, tokens[idx])

    md.core.ruler.after("inline", "obsidian-tasklists", fcn)
