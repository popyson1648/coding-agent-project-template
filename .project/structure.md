# Structure

## Top-level Directories

- `src/gentms`: CLI entry point, fiscal-year rules, and workbook generation logic
- `tests`: unit tests for fiscal-year mapping, workbook layout, and CLI behavior
- `.plans`: task plans
- `.decisions`: design and policy decisions
- `.project`: contributor-facing project documentation
- `scripts`: repository tooling such as verification

## Important Modules

- `src/gentms/cli.py`: command parsing and filesystem output behavior
- `src/gentms/fiscal.py`: fiscal-year month mapping and output naming rules
- `src/gentms/workbook.py`: Excel workbook, sheet, and validation generation

## Where To Make Changes

- Add CLI behavior in `src/gentms/cli.py`.
- Change fiscal-year or naming rules in `src/gentms/fiscal.py`.
- Change workbook columns, formatting, or validation in `src/gentms/workbook.py`.
- Keep tests in `tests/` aligned with each behavior change.

## Areas That Require Extra Care

- Do not change output naming or fiscal month resolution without updating tests and the decision record.
- Any workbook schema change must update the workbook tests and user-facing documentation together.
