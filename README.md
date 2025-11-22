# mdformat-obsidian

[![Build Status][ci-badge]][ci-link] [![PyPI version][pypi-badge]][pypi-link]

<!-- [![codecov.io][cov-badge]][cov-link]
[cov-badge]: https://codecov.io/gh/executablebooks/mdformat-obsidian/branch/main/graph/badge.svg
[cov-link]: https://codecov.io/gh/executablebooks/mdformat-obsidian
 -->

An [mdformat](https://github.com/executablebooks/mdformat) plugin for [Obsidian Flavored Markdown](https://help.obsidian.md/Editing+and+formatting/Obsidian+Flavored+Markdown).

## Features

- **[Callouts](https://help.obsidian.md/Editing+and+formatting/Callouts)** - Alert-style blocks with custom titles and folding
  - Supports all standard callout types (note, tip, warning, etc.)
  - Custom callout types with any identifier
  - Foldable callouts with `-` or `+` indicators
  - Nested callouts
  - Case-insensitive type matching (normalized to uppercase for compatibility)
- **Inline Footnotes** - Obsidian's `^[inline footnote]` syntax
- **Task Lists** - Extended checklist markers beyond `[x]` and `[ ]`
  - Supports `[?]`, `[/]`, `[-]`, and other custom markers
  - Preserves marker style during formatting
- **Dollar Math** - LaTeX math with `$...$` and `$$...$$` delimiters
  - Inline math: `$E=mc^2$`
  - Block math: `$$\n...\n$$`

> [!NOTE]
> The format for [GitHub Alerts](https://github.com/kyleking/mdformat-gfm-alerts) differs slightly from Obsidian callouts. Obsidian supports folding, custom titles, and is case-insensitive. For improved interoperability, this package normalizes callout types to uppercase (e.g., `[!tip]` → `[!TIP]`).

## `mdformat` Usage

Add this package wherever you use `mdformat` and the plugin will be auto-recognized. No additional configuration necessary. See [additional information on `mdformat` plugins here](https://mdformat.readthedocs.io/en/stable/users/plugins.html)

**Tip**: this package specifies an "extra" (`'recommended'`) for plugins that work well with `GFM`:

- [mdformat-beautysh](https://pypi.org/project/mdformat-beautysh)
- [mdformat-black](https://pypi.org/project/mdformat-black)
- [mdformat-config](https://pypi.org/project/mdformat-config)
- [mdformat-frontmatter](https://pypi.org/project/mdformat-frontmatter)
- [mdformat-simple-breaks](https://pypi.org/project/mdformat-simple-breaks)
- [mdformat-web](https://pypi.org/project/mdformat-web)
- [mdformat-wikilink](https://github.com/tmr232/mdformat-wikilink)

### Pre-Commit

```yaml
repos:
  - repo: https://github.com/executablebooks/mdformat
    rev: 0.7.18
    hooks:
      - id: mdformat
        additional_dependencies:
          - mdformat-obsidian
          # Or
          # - "mdformat-obsidian[recommended]"
```

### pipx

```sh
pipx install mdformat
pipx inject mdformat mdformat-obsidian
# Or
# pipx inject mdformat "mdformat-obsidian[recommended]"
```

## HTML Rendering

To generate HTML output, use `obsidian_plugin` from `mdit_plugins`. This combines all Obsidian-flavored markdown features (callouts, footnotes, task lists, math). For more details, see the [markdown-it-py documentation](https://markdown-it-py.readthedocs.io/en/latest/using.html#the-parser).

```py
from markdown_it import MarkdownIt
from mdformat_obsidian.mdit_plugins import obsidian_plugin

md = MarkdownIt()
md.use(obsidian_plugin)

text = "> [!tip] Callouts can have custom titles\n> Like this one."
md.render(text)
# <div>
# <div data-callout-metadata="" data-callout-fold="" data-callout="tip" class="callout">
# <div class="callout-title">
# <div class="callout-title-inner">Callouts can have custom titles</div>
# </div>
# <div class="callout-content">
# <p>Like this one.</p>
# </div>
# </div>
# </div>
```

**Accessibility Note:** For improved semantics, callouts are rendered as `<div>` elements rather than `<blockquote>`. The `>` syntax is repurposed for callouts (not quotations), so using div elements better represents the content structure. See [discussion on GitHub](https://github.com/orgs/community/discussions/16925#discussioncomment-8729846).

## Caveats

- **LaTeX Math**: Direct `\begin{...}` LaTeX environments are not supported. Use dollar math syntax (`$...$` or `$$...$$`) instead.
- **HTML Output Only**: The HTML rendering features are designed for programmatic HTML generation. For markdown-to-markdown formatting (the primary mdformat use case), these renderers are not invoked.
- **GitHub Compatibility**: While callouts work in both Obsidian and GitHub, subtle formatting differences exist. This plugin prioritizes Obsidian compatibility.

## Contributing

See [CONTRIBUTING.md](https://github.com/KyleKing/mdformat-obsidian/blob/main/CONTRIBUTING.md)

[ci-badge]: https://github.com/kyleking/mdformat-obsidian/workflows/CI/badge.svg?branch=main
[ci-link]: https://github.com/kyleking/mdformat-obsidian/actions?query=workflow%3ACI+branch%3Amain+event%3Apush
[pypi-badge]: https://img.shields.io/pypi/v/mdformat-obsidian.svg
[pypi-link]: https://pypi.org/project/mdformat-obsidian
