from __future__ import annotations

from markdown_it import MarkdownIt
from mdit_py_plugins.dollarmath import dollarmath_plugin
from mdit_py_plugins.footnote import footnote_plugin

from ._obsidian_callouts import obsidian_callout_plugin
from ._obsidian_task_lists import tasklists_plugin


def obsidian_plugin(md: MarkdownIt) -> None:
    """Plugin to parse Obsidian flavored Markdown."""
    md.use(dollarmath_plugin)
    md.use(footnote_plugin)
    md.use(obsidian_callout_plugin)
    md.use(tasklists_plugin)
