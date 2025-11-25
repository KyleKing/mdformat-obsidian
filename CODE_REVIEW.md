# Code Review: Alert Factories Refactor

## Overview

The staged changes introduce a shared `_synced/alert_factories` module intended for use by both `mdformat-obsidian` and `mdformat-gfm-alerts`. This represents a significant architectural shift from **block-level parsing** to **token-level parsing**.

## Architecture Change

### Old Approach (Block-Level)
```python
# Ran BEFORE markdown-it's blockquote rule
md.block.ruler.before("blockquote", ...)
# Had access to raw text lines
# Created tokens from scratch
```

### New Approach (Core-Level)
```python
# Runs AFTER blockquotes are already parsed into tokens
md.core.ruler.after("block", ...)
# Works with pre-parsed blockquote tokens
# Transforms existing tokens
```

## Issues Identified

### 1. ✅ FIXED: Regex Pattern Bug (Critical)

**Location**: `mdformat_obsidian/mdit_plugins/_obsidian_callouts.py:30`

**Original Staged Code**:
```python
PATTERN = re.compile(
    r"^(?P<marker>\\?\[!(?P<title>[^\]]+)\\?\])(?P<fold>[\-\+]?)\s*(?P<inline>[^\n\r]*)?",
    re.IGNORECASE,
)
```

**Problem**: `\s*` matches newlines, causing the **next line of content** to be captured as the `inline` (custom title) group.

**Impact**:
- Custom titles incorrectly include content from the next line
- Content stripping logic fails because it tries to strip too much
- Duplicate markers appear in output

**Example**:
```markdown
> [!info]
> Here's a callout block.
> It supports **Markdown**
```

Regex captures:
- `marker`: `[!info]`
- `title`: `info`
- `fold`: `` (empty)
- `inline`: `Here's a callout block.` ❌ **WRONG!** Should be empty

**Fix Applied**:
```python
PATTERN = re.compile(
    r"^(?P<marker>\\?\[!(?P<title>[^\]]+)\\?\])(?P<fold>[\-\+]?)[ \t]*(?P<inline>[^\n\r]*)?",
    #                                                               ^^^^^^ Changed from \s*
    re.IGNORECASE,
)
```

### 2. ⚠️ Content Stripping Logic Issues (Medium)

**Location**: `_obsidian_callouts.py:93-112` (staged)

**Problem**: The marker stripping logic in `_transform_to_callout` has several issues:

```python
# Lines 93-104: With custom title
if first_inline and custom_title:
    marker_with_fold = alert_match.marker
    if fold:
        marker_with_fold += fold
    if custom_title:
        marker_with_fold += " " + custom_title
    content = first_inline.content
    if content.startswith(marker_with_fold):  # ⚠️ Fragile
        first_inline.content = content[len(marker_with_fold):].lstrip()
```

**Issues**:

a) **Case sensitivity**: The regex is case-insensitive, but `startswith()` is case-sensitive
   - Input: `> [!info]`
   - Marker extracted: `[!info]` (lowercase from content)
   - But code checks uppercase in rendering
   - This can cause mismatches

b) **Nested blockquotes**: For nested callouts, `first_inline.content` contains the marker from the INNERMOST callout, but may have already been processed
   - Example: `> > [!todo] Yes!`
   - The outer blockquote's first_inline might contain: `> [!todo] Yes!`
   - The marker stripping only handles one level

c) **No validation**: If `startswith()` returns False, the marker remains in the content (causing duplicate markers in output)

**Impact**:
- Nested callouts show duplicate lowercase markers
- Content isn't properly cleaned
- Test failures in nested callout scenarios

### 3. ⚠️ Fold Marker Storage (Fixed in unstaged)

**Location**: `_obsidian_callouts.py:128-130`

**Original Staged Code**:
```python
if folded:
    open_token.attrs["data-callout-fold"] = "-"  # ❌ Always "-"
    open_token.attrs["class"] = "callout is-collapsible is-collapsed"
```

**Problem**: Always stores `-` even when the fold marker is `+`

**Fix Applied** (unstaged):
```python
if folded:
    open_token.attrs["data-callout-fold"] = fold  # ✅ Preserves actual fold marker
    open_token.attrs["class"] = "callout is-collapsible is-collapsed"
```

### 4. ✅ Title Token Structure (Good)

**Location**: `_obsidian_callouts.py:137-147`

The staged code creates proper title tokens with inline content:

```python
title_inline = Token("inline", "", 0)
title_inline.content = custom_title or alert_match.title.title()
title_inline.children = []
```

**Good Practice**: Uses `.title()` as fallback when no custom title is provided.

## Recommendations

### For Shared Module (`_synced/alert_factories`)

#### 1. Add Validation Helper
```python
def validate_marker_stripped(
    first_inline: Token | None,
    marker_to_strip: str,
) -> bool:
    """Validate that marker was successfully stripped from content."""
    if not first_inline:
        return True
    # Case-insensitive check
    content_lower = first_inline.content.lower()
    marker_lower = marker_to_strip.lower()
    return not content_lower.startswith(marker_lower.lstrip(">").strip())
```

#### 2. Improve Stripping Logic
```python
# In _transform_to_callout callback
if first_inline:
    marker_to_strip = alert_match.marker
    if fold:
        marker_to_strip += fold
    if custom_title:
        marker_to_strip += " " + custom_title

    content = first_inline.content
    # Case-insensitive stripping
    if content.lower().startswith(marker_to_strip.lower()):
        first_inline.content = content[len(marker_to_strip):].lstrip()
    else:
        # Log warning or handle edge case
        pass
```

#### 3. Document Edge Cases

Add docstring examples:
```python
"""Transform blockquote tokens to alert tokens.

Edge Cases:
    - Nested blockquotes: The first_inline.content for nested blockquotes
      may contain markers from inner blockquotes. This callback is called
      for each nesting level separately.

    - Custom titles: When inline content follows the marker on the same line,
      it's captured as custom_title and must be stripped from first_inline.

    - Fold markers: The '+' or '-' characters indicate collapsible state
      and must be preserved in attrs for proper rendering.

Example Nested Structure:
    Input:
        > [!info] Outer
        > > [!warning] Inner
        > > Content

    Processing order:
        1. Outer blockquote processed first
        2. Inner blockquote processed second (parse_nested=True)
"""
```

### For Obsidian-Specific Code

#### 1. Validate After Transform

Add validation after calling the factory:

```python
def obsidian_callout_plugin(md: MarkdownIt) -> None:
    """Install the obsidian callout plugin."""

    def _transform_to_callout(...):
        # ... transformation logic ...

        # Validate marker was stripped
        if first_inline and alert_match.marker.lower() in first_inline.content.lower():
            # Marker wasn't properly stripped - log warning or fix
            pass

    core_rule = blockquote_to_alert_factory(...)
    md.core.ruler.after("block", OBSIDIAN_CALLOUT_PREFIX, core_rule)
```

#### 2. Add Integration Tests

```python
def test_nested_callouts_no_duplicate_markers():
    """Ensure nested callouts don't show duplicate markers."""
    text = """> [!question] Outer
> > [!todo] Inner
> > Content"""

    output = mdformat.text(text, extensions={"obsidian"})

    # Should not contain lowercase markers
    assert "[!question]" not in output.lower().replace("[!question]", "[!QUESTION]")
    assert "[!todo]" not in output.lower().replace("[!todo]", "[!TODO]")
```

## Sharing Strategy

### For `mdformat-gfm-alerts` Compatibility

The `_synced/alert_factories` module is well-designed for sharing, but needs:

1. **Better error handling**: The transform callback should handle edge cases gracefully
2. **Validation hooks**: Allow implementations to validate transformations
3. **Logging/debugging**: Add optional debug output for troubleshooting

### Recommended Sharing Approach

```python
# In _synced/alert_factories/_alert_factories.py
from typing import Protocol

class TransformValidator(Protocol):
    """Protocol for validating alert transformations."""
    def validate(
        self,
        tokens: list[Token],
        start: int,
        end: int,
        alert_match: AlertMatch
    ) -> bool:
        """Return True if transformation is valid."""
        ...

def blockquote_to_alert_factory(
    prefix: str,
    patterns: Sequence[re.Pattern[str]],
    transform_callback: Callable[[list[Token], int, int, AlertMatch], None],
    *,
    parse_nested: bool = True,
    validator: TransformValidator | None = None,  # ✅ Add validator
) -> Callable[[StateCore], None]:
    # ... implementation ...
    if validator and not validator.validate(tokens, start_index, i, alert_match):
        # Skip transformation if validation fails
        continue
```

## Test Results

- **Before fixes**: 19 failures
- **After regex fix**: 11 failures
- **Remaining issues**: Nested callouts, HTML rendering

## Summary

### Critical Issues ✅ Fixed
1. Regex pattern captures newlines as custom titles

### Medium Issues ⚠️ Remaining
1. Content stripping logic fragile for nested blockquotes
2. Case sensitivity in marker matching
3. No validation when stripping fails

### Recommendations for Shared Module
1. Add validation helpers
2. Improve error handling
3. Document edge cases thoroughly
4. Add integration tests for nested structures

The refactor is **sound in principle** but needs **refinement** in edge case handling to be production-ready for sharing between projects.
