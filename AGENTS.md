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
tox -e test -- --exitfirst --failed-first --new-first -vv --snapshot-update
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

The package implements mdformat's plugin interface with up to four key exports in `__init__.py`:

- `update_mdit`: Registers markdown-it parser extensions
- `add_cli_argument_group`: Optionally adds CLI flags
- `RENDERERS`: Maps syntax tree node types to render functions
- `POSTPROCESSORS`: Post-processes rendered output (list normalization, inline wrapping, deflist escaping)

### Core Components

**mdformat_obsidian/plugin.py**

- Entry point that configures the mdformat plugin, registers all mdit_plugins, defines custom renders, and handles CLI configuration options

### Configuration Options

Configuration can be passed via:

1. Example CLI arguments: `--cli-argument`
1. Example TOML config file (`.mdformat.toml`):
    ```toml
    [plugin.obsidian]
    cli_argument = true
    ```
1. API: `mdformat.text(content, extensions={"obsidian"}, options={...})`

### Testing Strategy

**Snapshot Testing**

- Test fixtures in `tests/format/fixtures/` and `tests/render/fixtures/`
- Main test file: `tests/test_mdformat.py` verifies idempotent formatting against `tests/pre-commit-test.md`

**Test Organization**

- `tests/format/`: Tests formatting output (input markdown → formatted markdown)
- `tests/render/`: Tests HTML rendering (markdown → HTML via markdown-it)

## Development Notes

- **Do not use `uv` commands**—there is no `uv.lock` file. Always use `tox` (installed via mise and available on PATH) which manages environments and dependencies.
