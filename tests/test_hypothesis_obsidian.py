"""Property-based idempotency tests for Obsidian-specific syntax.

This file is project-specific (unlike tests/test_hypothesis.py, which is
synced from the shared copier template) and extends the generic building
blocks with callouts, extended task-list marks, footnotes, and dollar math.
It also covers the obsidian+gfm interop regression from issue #11: standard
task marks must stay idempotent when mdformat-gfm's tasklist rule is also
active, regardless of which plugin's core rule registers first.
"""

from __future__ import annotations

import os

import mdformat
from hypothesis import HealthCheck, given, settings
from hypothesis import strategies as st

from tests.test_hypothesis import bracketed_inline, bullet_list, fenced_code_block

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


@st.composite
def callout_block(draw: st.DrawFn) -> str:
    kind = draw(st.sampled_from(["note", "tip", "warning", "danger", "info", "faq"]))
    fold = draw(st.sampled_from(["", "-", "+"]))
    title = draw(st.one_of(st.just(""), _SAFE_TEXT.map(lambda t: f" {t}")))
    body = draw(_SAFE_TEXT)
    return f"> [!{kind}]{fold}{title}\n> {body}"


@st.composite
def tasklist_block(draw: st.DrawFn) -> str:
    mark = draw(st.sampled_from([" ", "x", "X", "/", "-", "?"]))
    text = draw(_SAFE_TEXT)
    return f"- [{mark}] {text}"


@st.composite
def footnote_block(draw: st.DrawFn) -> str:
    label = draw(
        st.text(alphabet=st.characters(whitelist_categories=("L",)), min_size=1)
    )
    body = draw(_SAFE_TEXT)
    reference = draw(_SAFE_TEXT)
    return f"{reference}[^{label}]\n\n[^{label}]: {body}"


@st.composite
def dollar_math_block(draw: st.DrawFn) -> str:
    expr = draw(st.sampled_from(["a^2 + b^2 = c^2", "x = y + z", "\\frac{a}{b}"]))
    return f"$${expr}$$"


@st.composite
def markdown_document(draw: st.DrawFn) -> str:
    block_strategy = st.one_of(
        bullet_list(),
        bracketed_inline(),
        fenced_code_block(),
        callout_block(),
        tasklist_block(),
        footnote_block(),
        dollar_math_block(),
    )
    blocks = draw(st.lists(block_strategy, min_size=1, max_size=5))
    return "\n\n".join(blocks)


@given(markdown_document())
def test_idempotency_obsidian_only(text: str) -> None:
    once = mdformat.text(text, extensions={"obsidian"})
    twice = mdformat.text(once, extensions={"obsidian"})
    assert once == twice


@given(markdown_document())
def test_idempotency_with_gfm(text: str) -> None:
    """Regression test for #11: obsidian+gfm interop must stay idempotent."""
    once = mdformat.text(text, extensions=["obsidian", "gfm", "tables"])
    twice = mdformat.text(once, extensions=["obsidian", "gfm", "tables"])
    assert once == twice


@given(st.sampled_from([" ", "x", "X"]), _SAFE_TEXT)
def test_standard_task_marks_never_escaped_with_gfm(mark: str, text: str) -> None:
    """Regression test for #11: standard GFM marks must render unescaped."""
    output = mdformat.text(
        f"- [{mark}] {text}", extensions=["obsidian", "gfm", "tables"]
    )
    assert "\\[" not in output
