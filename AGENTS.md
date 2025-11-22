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

- This project uses `uv-build` as the build backend
- Uses `tox` for test automation with multiple Python versions (3.10, 3.14)
- Pre-commit is configured but the project now uses `prek` (faster alternative)
- Python 3.10+ is required (see `requires-python` in `pyproject.toml`)
- Version is defined in `mdformat_obsidian/__init__.py` as `__version__`
