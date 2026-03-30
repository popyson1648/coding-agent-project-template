# Testing

## Test Types

- `pytest` unit tests for fiscal-year resolution, workbook generation, and CLI behavior
- `mypy` static type checks for application, tests, and verification script
- `ruff` formatting and lint checks
- `compileall` as a lightweight build sanity check

## Minimum Checks Before Completion

- `python3 scripts/verify.py`

## Checks By Change Type

- CLI behavior: run `python3 -m pytest tests/test_cli.py`
- Fiscal-year or naming logic: run `python3 -m pytest tests/test_fiscal.py`
- Workbook layout or validation: run `python3 -m pytest tests/test_workbook.py`
- Type changes or signature changes: run `python3 -m mypy`
- Broad changes: run `python3 scripts/verify.py`

## How To Run Verification

- Full verification: `python3 scripts/verify.py`
- List configured phases: `python3 scripts/verify.py --list`
