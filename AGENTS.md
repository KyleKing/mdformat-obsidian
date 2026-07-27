# AGENTS.md

## Testing

```bash
# Run all tests using tox
tox

# Run tests with coverage (Python 3.14 - current version)
tox -e test

# Run tests with coverage (Python 3.10 - minimum version)
tox -e test-min

# Run specific tests with pytest flags
tox -e test -- --exitfirst --failed-first --new-first -vv
# Add --snapshot-update too if the project has a snapshot library (e.g. syrupy) configured
```

## Linting and Formatting

```bash
# Run all pre-commit hooks (using prek)
tox -e prek
# Or run directly with prek
prek run --all

# Run ruff for linting and formatting
tox -e ruff
# With unsafe fixes
tox -e ruff -- --unsafe-fixes
```

## Type Checking

```bash
# Run mypy type checking
tox -e type
```

## Canary Testing (Real Downstream Repos)

```bash
# Run idempotency checks against all tracked downstream repos
tox -e canary

# Test a subset by name
tox -e canary -- some-repo another-repo
```

Clones real consumer repos via git sparse checkout and runs a two-pass idempotency check: format once, format again, compare. Not part of the default `tox` run, so invoke it before releasing. Configure tracked repos in `scripts/canary_repos.json`.

## Pre-commit Hook Testing

```bash
# Test the plugin as a pre-commit hook
tox -e hook-min
```

## One-Off Testing

```bash
# Create a development environment with local code installed
tox devenv .venv

# Test mdformat on inline content
echo '- \[test\]: value' | .venv/bin/mdformat - --extension obsidian 2>&1

# Test mdformat on a specific file
.venv/bin/mdformat tests/pre-commit-test.md --extension obsidian

# Run Python code with local package installed
.venv/bin/python3 << 'PYTHON'
import mdformat
output = mdformat.text("- \[test\]: value", extensions={"obsidian"})
print(output)
PYTHON
```

## Architecture

### Plugin System

The package implements mdformat's plugin interface with up to four exports in `__init__.py`:

- `update_mdit`: Registers markdown-it parser extensions
- `add_cli_argument_group`: Optionally adds CLI flags
- `RENDERERS`: Maps syntax tree node types to render functions
- `POSTPROCESSORS`: Post-processes rendered output of a syntax node. Multiple plugins can register a postprocessor for the same node type, and they run in series

### Core Components

**mdformat_obsidian/plugin.py**

- Entry point that configures the mdformat plugin, registers all mdit_plugins, defines custom renders, and handles CLI configuration options

### Configuration Options

Configuration can be passed via:

1. CLI argument, e.g. the scaffolded `--argument` flag
1. TOML config file (`.mdformat.toml`):
    ```toml
    [plugin.obsidian]
    argument = true
    ```
1. API: `mdformat.text(content, extensions={"obsidian"}, options={...})`

Two footguns to avoid:

- Boolean flags in `add_cli_argument_group` must use `action="store_const", const=True` (default `None`), not `store_true`. A `store_true` default (`False`) is indistinguishable from an explicit choice to `get_conf()`, so it silently overrides `argument = true` from `.mdformat.toml` whenever the CLI flag isn't passed. mdformat's CLI builder raises a `DeprecationWarning` for any plugin flag whose default isn't `None` or `argparse.SUPPRESS`
- Read config lazily. Call `get_conf()` (or read `RenderContext.options`) inside the rule/renderer function itself, not inside `update_mdit`. mdformat runs extensions' `update_mdit` in an unguaranteed order, so a value captured there can be stale by the time every extension has finished configuring options

### Testing Strategy

**Fixture Testing**

- Fixture files (before/after markdown pairs) live in `tests/format/fixtures/` and `tests/render/fixtures/`, parsed with `markdown_it.utils.read_fixture_file`
- `tests/test_mdformat.py` verifies idempotent formatting against `tests/pre-commit-test.md`
- A downstream project may layer a snapshot library (e.g. syrupy) on top of these fixtures; check `pyproject.toml` before assuming `--snapshot-update` applies

**Test Organization**

- `tests/format/`: Tests formatting output (input markdown → formatted markdown)
- `tests/render/`: Tests HTML rendering (markdown → HTML via markdown-it)
- `tests/test_hypothesis.py`: Property-based idempotency testing over generated markdown documents

## Development Notes

- Do not use `uv` commands (there is no `uv.lock` file). Always use `tox` (installed via mise and available on PATH), which manages environments and dependencies
