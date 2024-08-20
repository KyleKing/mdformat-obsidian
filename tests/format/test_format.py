from __future__ import annotations

from itertools import chain
from pathlib import Path
from typing import TypeVar

import mdformat
import pytest
from markdown_it.utils import read_fixture_file

from tests.helpers import print_text

T = TypeVar("T")


def flatten(nested_list: list[list[T]]) -> list[T]:
    return [*chain(*nested_list)]


fixtures = flatten(
    [
        read_fixture_file(Path(__file__).parent / "fixtures" / fixture_path)
        for fixture_path in (
            "dollar_math.md",
            "obsidian_callouts.md",
            "obsidian_inline_footnotes.md",
            "obsidian_task_lists.md",
        )
    ],
)


@pytest.mark.parametrize(
    ("line", "title", "text", "expected"),
    fixtures,
    ids=[f[1] for f in fixtures],
)
def test_material_content_tabs_fixtures(line, title, text, expected):
    output = mdformat.text(text, extensions={"obsidian"})
    print_text(output, expected)
    assert output.rstrip() == expected.rstrip()
