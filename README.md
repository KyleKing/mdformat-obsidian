# mdformat-gfm-alerts

[![Build Status][ci-badge]][ci-link] [![PyPI version][pypi-badge]][pypi-link]

<!-- [![codecov.io][cov-badge]][cov-link]
[cov-badge]: https://codecov.io/gh/executablebooks/mdformat-gfm-alerts/branch/main/graph/badge.svg
[cov-link]: https://codecov.io/gh/executablebooks/mdformat-gfm-alerts
 -->

An [mdformat](https://github.com/executablebooks/mdformat) plugin for [GitHub "Alerts"](https://docs.github.com/en/get-started/writing-on-github/getting-started-with-writing-and-formatting-on-github/basic-writing-and-formatting-syntax#alerts). "Alerts" are a block quote variation of admonitions that were proposed in this [community discussion](https://github.com/orgs/community/discussions/16925) and are currently a separate extension of the [GFM (GitHub-Flavored Markdown) syntax](https://github.github.com/gfm).

## `mdformat` Usage

Add this package wherever you use `mdformat` and the plugin will be auto-recognized. No additional configuration necessary. See [additional information on `mdformat` plugins here](https://mdformat.readthedocs.io/en/stable/users/plugins.html)

### Pre-Commit

```yaml
repos:
  - repo: https://github.com/executablebooks/mdformat
    rev: 0.7.16
    hooks:
      - id: mdformat
        additional_dependencies:
          - mdformat-gfm-alerts
```

### pipx

```sh
pipx install mdformat
pipx inject mdformat mdformat-gfm-alerts
```

## HTML Rendering

To generate HTML output, `gfm_alerts_plugin` can be imported from `mdit_plugins`. For more guidance on `MarkdownIt`, see the docs: <https://markdown-it-py.readthedocs.io/en/latest/using.html#the-parser>

```py
from markdown_it import MarkdownIt

from mdformat_gfm_alerts.mdit_plugins import gfm_alerts_plugin

md = MarkdownIt()
md.use(gfm_alerts_plugin)

text = "> [!NOTE]\n> Useful information that users should know, even when skimming content. "
md.render(text)
# <blockquote>
# <div class="markdown-alert markdown-alert-note">
# <p class="markdown-alert-title">Note</p>
# <p>Useful information that users should know, even when skimming content.</p>
# </div>
# </blockquote>
```

> [!WARNING]
> This package does not properly handle replacing the `blockquote` outer `div` with a `div` for accessibility. This should be possible with `markdown-it`, but I haven't yet found a way.

## Contributing

See [CONTRIBUTING.md](https://github.com/KyleKing/mdformat-gfm-alerts/blob/main/CONTRIBUTING.md)

[ci-badge]: https://github.com/kyleking/mdformat-gfm-alerts/workflows/CI/badge.svg?branch=main
[ci-link]: https://github.com/kyleking/mdformat-gfm-alerts/actions?query=workflow%3ACI+branch%3Amain+event%3Apush
[pypi-badge]: https://img.shields.io/pypi/v/mdformat-gfm-alerts.svg
[pypi-link]: https://pypi.org/project/mdformat-gfm-alerts
