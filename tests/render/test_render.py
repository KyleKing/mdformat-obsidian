from pathlib import Path

import pytest
from markdown_it import MarkdownIt
from markdown_it.utils import read_fixture_file

from mdformat_obsidian.mdit_plugins import (
    footnote_plugin,
    obsidian_callout_plugin,
    tasklists_plugin,
)
from tests.helpers import print_text

FIXTURE_PATH = Path(__file__).parent / "fixtures"


def with_plugin(filename, plugins):
    return [(*fix, plugins) for fix in read_fixture_file(FIXTURE_PATH / filename)]


@pytest.mark.parametrize(
    ("line", "title", "text", "expected", "plugins"),
    [
        *with_plugin("obsidian_callouts.md", [obsidian_callout_plugin]),
        *with_plugin("obsidian_inline_footnotes.md", [footnote_plugin]),
        *with_plugin("obsidian_task_lists.md", [tasklists_plugin]),
    ],
)
def test_render(line, title, text, expected, plugins):
    md = MarkdownIt("commonmark")
    for plugin in plugins:
        md.use(plugin)
    if "DISABLE-CODEBLOCKS" in title:
        md.disable("code")
    md.options["xhtmlOut"] = False
    output = md.render(text)
    print_text(output, expected, show_whitespace=False)
    assert output.rstrip() == expected.rstrip()
