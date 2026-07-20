# Dollarmath idempotency investigation

Notes from investigating and fixing dollarmath (`$$...$$`) idempotency bugs surfaced by canary-testing this plugin against a real-world Obsidian vault (`ryandeardorff/public-notes`). Kept here since the investigation crossed into other local repos (`mdformat-mkdocs`) whose findings aren't otherwise recorded anywhere in this repo.

## Bugs found and fixed

All four are fixed in `mdformat_obsidian/plugin.py` and `mdformat_obsidian/mdit_plugins/_obsidian_dollarmath.py`, with regression tests in `tests/test_hypothesis_obsidian.py::test_dollarmath_idempotency_regressions`.

1. **Block math nested in a list item** (`- $$\n  x\n  $$`) grew 2 spaces of indentation per format pass.
1. **Block math nested in a blockquote** (`> $$\n> x\n> $$`) grew an extra `>` marker per format pass.
1. **Multi-line math with internal-line indentation** (e.g. `\begin{align}...\end{align}` spanning several lines inside a list item) — same growth as (1), but only visible with 2+ content lines.
1. **Same-line-closed math with trailing text** (`$$b$$ Binomial`) — `mdit_py_plugins.dollarmath`'s block rule only recognizes a same-line close when the closing `$$` is the last thing on the line. With trailing text after it, the rule instead scans forward for the *next* `$$` anywhere in the document, silently swallowing everything in between (including subsequent list items) as literal math content.

## Root causes

Bugs 1-3: `node.content` for a `math_block` token retains the *raw source indentation* of continuation lines (list-item indent, blockquote `> ` prefix). The renderer was returning that content verbatim, so the indentation was embedded in the child's rendered text. mdformat's list-item/blockquote wrappers then apply their *own* indentation on top of that on every render pass, compounding it.

Bug 4 is a distinct, upstream parser ambiguity in `mdit_py_plugins.dollarmath`'s block rule (`math_block_dollar` in `dollarmath/index.py`, ~line 320): the same-line-close check is `lineText.strip().endswith("$$")`, which fails whenever there's any trailing content after the closing delimiter.

## Fix

- **Bugs 1-3**: `_split_math_block_content()` in `plugin.py` now runs `textwrap.dedent()` (plus blockquote-marker stripping and leading/trailing whitespace normalization) on `node.content` before wrapping it back in `$$`, so raw source indentation is discarded rather than passed through to be re-applied by the list/blockquote wrapper.
- **Bug 4**: `obsidian_dollarmath_plugin()` in `mdit_plugins/_obsidian_dollarmath.py` wraps `dollarmath_plugin`'s block rule and rejects the match outright when a line opens `$$`, closes it later on the same line, but has trailing content after that close. The line then falls through to normal paragraph/inline parsing — correct and stable, since a single source line can't otherwise be split between a closed math span and trailing paragraph text within markdown-it's line-based block model.

## Dead end: porting `mdformat-mkdocs`'s fix wholesale

`mdformat-mkdocs` has equivalent-looking math renderer code (`_split_math_block_content`/`_strip_blockquote_markers` in its `plugin.py`) and appeared to fully solve bug 4 in testing. It doesn't, on its own — it has the same underlying parse-time swallowing bug (confirmed by inspecting the token stream directly: identical to this plugin's, pre-fix). Its apparent stability comes from a large, separate `_normalize_list.py` module (~540 lines) that completely overrides `ordered_list`/`bullet_list` rendering, recomputing list indentation from the *rendered text* rather than trusting the naive per-line indent. That module exists for mkdocs-specific concerns (definition lists, Material admonitions, content tabs, a fixed 4-space indent width) and even with it, the swallowed `3)` line is still absorbed as literal math content rather than becoming its own list item — it just doesn't grow unboundedly.

Porting that subsystem here to fix a dollarmath edge case would have been disproportionate and would import unrelated mkdocs-specific concepts. The parser-level guard (bug 4's fix, above) is the smaller, more correct fix: it prevents the corruption at its source instead of masking the symptom in a general-purpose list renderer.

## Known remaining limitation (not fixed)

None currently known for dollarmath. If a new non-idempotent case turns up via canary testing, re-run `tox -e canary -- ryandeardorff-public-notes` to reproduce against real content, and check with `textwrap.dedent()` first — it's the likely culprit for any list/blockquote-nested case that isn't yet dedented correctly.
