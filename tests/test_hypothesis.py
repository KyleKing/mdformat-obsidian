"""Property-based idempotency tests using Hypothesis.

Generates random markdown documents from common building blocks (lists,
links, fenced code) and checks that formatting is idempotent: formatting
once and formatting twice must produce the same output. Add plugin-specific
composite strategies to `markdown_document` below to cover
'obsidian' syntax.
"""

from __future__ import annotations

import os

import mdformat
from hypothesis import HealthCheck, given, settings
from hypothesis import strategies as st

settings.register_profile(
    "ci",
    max_examples=50,
    suppress_health_check=[HealthCheck.too_slow, HealthCheck.filter_too_much],
)
settings.register_profile("dev", max_examples=25)
settings.load_profile(os.environ.get("HYPOTHESIS_PROFILE", "ci"))

_SAFE_TEXT = st.text(
    alphabet=st.characters(whitelist_categories=("L", "N")),
    min_size=1,
)

_MAX_LIST_DEPTH = 3


@st.composite
def bullet_list(draw: st.DrawFn, depth: int = 1) -> str:
    indent = "    " * (depth - 1)
    items = draw(st.lists(_SAFE_TEXT, min_size=1, max_size=3))
    lines: list[str] = []
    for item in items:
        lines.append(f"{indent}- {item}")
        if depth < _MAX_LIST_DEPTH and draw(st.booleans()):
            nested = draw(bullet_list(depth=depth + 1))
            lines.append(nested)
    return "\n".join(lines)


@st.composite
def numbered_list(draw: st.DrawFn, depth: int = 1) -> str:
    indent = "    " * (depth - 1)
    items = draw(st.lists(_SAFE_TEXT, min_size=1, max_size=3))
    lines: list[str] = []
    for i, item in enumerate(items, start=1):
        lines.append(f"{indent}{i}. {item}")
        if depth < _MAX_LIST_DEPTH and draw(st.booleans()):
            nested = draw(numbered_list(depth=depth + 1))
            lines.append(nested)
    return "\n".join(lines)


@st.composite
def bracketed_inline(draw: st.DrawFn) -> str:
    text = draw(st.one_of(st.just("{attr}"), st.just("\\[escaped\\]"), _SAFE_TEXT))
    return f"[{text}](https://example.com)"


@st.composite
def fenced_code_block(draw: st.DrawFn) -> str:
    lang = draw(st.sampled_from(["python", "bash", "text", ""]))
    content = draw(_SAFE_TEXT)
    return f"```{lang}\n{content}\n```"


@st.composite
def markdown_document(draw: st.DrawFn) -> str:
    block_strategy = st.one_of(
        bullet_list(),
        numbered_list(),
        bracketed_inline(),
        fenced_code_block(),
    )
    blocks = draw(st.lists(block_strategy, min_size=1, max_size=5))
    return "\n\n".join(blocks)


@given(markdown_document())
def test_idempotency(text: str) -> None:
    once = mdformat.text(text, extensions={"obsidian"})
    twice = mdformat.text(once, extensions={"obsidian"})
    assert once == twice
