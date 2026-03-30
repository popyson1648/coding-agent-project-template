# Decision

## Title

Use Python with openpyxl for the gentms CLI and fiscal-year workbook generation.

## Date

2026-03-30

## Status

Accepted

## Decision

- Implement the tool as a Python package in `src/gentms`.
- Use `argparse` for the CLI surface.
- Use `openpyxl` to generate `.xlsx` files, date formatting, and dropdown validation.
- Name annual outputs with the fiscal year and era short code, such as `2026年度(R8).xlsx`.
- Name monthly outputs with the resolved calendar year and month, such as `2027-01.xlsx`.
- Resolve fiscal months as April to December in the given year and January to March in the following year.
- Resolve the era short code from the fiscal-year start date so boundary years follow the actual era in effect on April 1.

## Context

The repository started as a documentation scaffold and did not yet contain application code or a dependency stack. The requested tool must generate native Excel workbooks with per-cell formatting and validation rules.

## Alternatives

- Generate raw XLSX XML directly without a spreadsheet library.
- Use another language and spreadsheet package.
- Emit CSV instead of `.xlsx`.

## Reason

Python is already available in local and CI environments, `argparse` keeps the CLI dependency surface small, and `openpyxl` provides the required workbook features with minimal implementation overhead.

## Consequences

- The project now needs a Python package definition and an `openpyxl` dependency.
- Verification and CI need Python-oriented commands.
- The workbook layout and validation behavior can be tested directly with Python tests.

## Revisit Conditions

Revisit this decision if the tool needs distribution requirements that Python packaging cannot meet cleanly, or if workbook generation grows beyond what `openpyxl` handles maintainably.
