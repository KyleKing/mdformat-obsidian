# mdformat-obsidian

[![Build Status][ci-badge]][ci-link] [![PyPI version][pypi-badge]][pypi-link]

<!-- [![codecov.io][cov-badge]][cov-link]
[cov-badge]: https://codecov.io/gh/executablebooks/mdformat-obsidian/branch/main/graph/badge.svg
[cov-link]: https://codecov.io/gh/executablebooks/mdformat-obsidian
 -->

An [mdformat](https://github.com/executablebooks/mdformat) plugin for [Obsidian Flavored Markdown](https://help.obsidian.md/Editing+and+formatting/Obsidian+Flavored+Markdown). This plugin directly supports [Callouts](https://help.obsidian.md/Editing+and+formatting/Callouts), inline footnotes, task lists with custom markers, and dollar math. See the test directory for supported formats.

> [!NOTE]
> The format for [GitHub Alerts](https://github.com/kyleking/mdformat-gfm-alerts) differs slightly from Obsidian, so they are not fully compatible. Obsidian supports folding, custom titles, and is case insensitive. To improve interoperability, this package makes the stylistic choice of capitalizing the text within `[!...]`.

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

To generate HTML output, `obsidian_plugin` can be imported from `mdit_plugins`. For more guidance on `MarkdownIt`, see the docs: <https://markdown-it-py.readthedocs.io/en/latest/using.html#the-parser>

```py
from markdown_it import MarkdownIt

from mdformat_obsidian.mdit_plugins import obsidian_plugin

md = MarkdownIt()
md.use(obsidian_plugin)

text = "> [!tip] Callouts can have custom titles\n> Like this one."
md.render(text)
# <blockquote>
# <div data-callout-metadata="" data-callout-fold="" data-callout="tip" class="callout">
# <div class="callout-title">
# <div class="callout-title-inner">Callouts can have custom titles</div>
# </div>
# <div class="callout-content">
# <p>Like this one.</p>
# </div>
# </div>
# </blockquote>
```

> [!WARNING]
> The outer `<blockquote>` tag is preserved to maintain compatibility with standard Markdown parsers. For full accessibility, you may want to replace this with a `<div>` in post-processing, as the `>` blockquote syntax is being repurposed for callouts.

## Contributing

See [CONTRIBUTING.md](https://github.com/KyleKing/mdformat-obsidian/blob/main/CONTRIBUTING.md)

[ci-badge]: https://github.com/kyleking/mdformat-obsidian/workflows/CI/badge.svg?branch=main
[ci-link]: https://github.com/kyleking/mdformat-obsidian/actions?query=workflow%3ACI+branch%3Amain+event%3Apush
[pypi-badge]: https://img.shields.io/pypi/v/mdformat-obsidian.svg
[pypi-link]: https://pypi.org/project/mdformat-obsidian
