# Build

## Prerequisites

- Python 3.11 or later
- `pip`

## Setup

- Install runtime and development dependencies with `python3 -m pip install -e .[dev]`

## Build

- Run `python3 -m compileall src tests scripts`
- Run `python3 -m mypy`

## Run

- Installed entry point: `gentms annual 2026`
- Module form: `python3 -m gentms annual 2026`
- Shorthand annual form: `python3 -m gentms 2026`
- Monthly output: `python3 -m gentms monthly 2026 12 1 2 3`

## Common Failures

- `ModuleNotFoundError: openpyxl`: install dependencies again.
- `output path already exists`: remove or rename the conflicting file or directory, then rerun the command.
- `duplicate months are not allowed`: remove repeated month arguments.
