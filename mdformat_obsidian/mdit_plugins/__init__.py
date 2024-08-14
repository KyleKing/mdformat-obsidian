from mdit_py_plugins.footnote import footnote_plugin

from ._obsidian_callouts import (
    INLINE_SEP,
    OBSIDIAN_CALLOUT_PREFIX,
    format_obsidian_callout_markup,
    obsidian_callout_plugin,
)
from ._obsidian_inline_footnotes import (
    format_footnote,
    format_footnote_block,
    format_footnote_ref,
)

__all__ = (
    "INLINE_SEP",
    "OBSIDIAN_CALLOUT_PREFIX",
    "footnote_plugin",
    "format_footnote",
    "format_footnote_block",
    "format_footnote_ref",
    "format_obsidian_callout_markup",
    "obsidian_callout_plugin",
)
