# Plan

## Goal

Create a CLI tool named `gentms` that generates annual or monthly Excel workbooks for a Japanese fiscal year timesheet workflow.

## Scope

- Implement a CLI entry point for annual and monthly generation.
- Generate `.xlsx` files with the approved schema and month layout.
- Apply Excel date cells, display formatting, and dropdown validation rules.
- Handle fiscal-year month-to-year mapping for April to March.
- Reject invalid input and reject output when target files or directories already exist.
- Add or update tests and repository verification so the feature can be checked locally and in CI.
- Refresh project documentation that describes how to use and verify the tool.

## Non-goals

- Editing or merging into existing `.xlsx` files.
- Overwrite or force-write support.
- Support for holiday types beyond `年休` and `忌引`.
- Packaging or publishing beyond what is needed for local repository use.

## Assumptions

- Column names are fixed as `日付`, `出勤 (時)`, `出勤 (分)`, `退勤 (時)`, `退勤 (分)`, `休暇種別`.
- `日付` is stored as an Excel date value and displayed with format `d`.
- Time fields are stored as strings and use dropdown candidates only.
- `annual` creates one workbook named like `2026年度(R8).xlsx`.
- `monthly` creates one workbook per requested month, keeps the user-specified month order, and treats duplicate months as an error.
- `--create-dir` applies to both `annual` and `monthly` and fails if the target directory already exists.
- The implementation language and Excel library will be chosen based on the current repository/tooling state during implementation.

## Steps

1. Inspect the current repository tooling, choose the implementation stack, and record any structural decision that needs to be preserved.
2. Scaffold the CLI application layout and dependency configuration without creating unnecessary root-level files.
3. Implement fiscal-year date generation, Japanese era workbook naming, and workbook/sheet naming rules.
4. Implement worksheet generation with the approved columns, per-month row counts, date formatting, and dropdown validation.
5. Implement CLI argument parsing for:
   - `gentms annual <year>`
   - `gentms annual <year> --create-dir`
   - `gentms monthly <year> <month...>`
   - `gentms monthly <year> <month...> --create-dir`
6. Implement validation and failure behavior for invalid years, invalid months, duplicate months, and existing output paths.
7. Add tests that cover fiscal-year mapping, workbook naming, monthly selection behavior, and output-path conflict handling.
8. Update `.project/` documents, `.project/verification.toml`, `.pre-commit-config.yaml`, and `.github/workflows/ci.yml` to match the actual implementation and verification flow.
9. Run repository verification, review the generated changes for consistency, and fix any issue before completion.

## Verification

- Run `python3 scripts/verify.py` after `.project/verification.toml` is populated with real commands.
- Run targeted tests for date generation, workbook generation, and CLI argument handling.
- If practical, generate sample workbooks and inspect them programmatically to confirm:
  - sheet order
  - row counts per month
  - date cell values and display format
  - dropdown validation presence on the expected columns
  - error behavior when outputs already exist

## Open Issues

- The implementation stack is not yet selected because the repository does not currently contain application code.
- The exact repository layout for the CLI package should be aligned with the chosen stack before code is added.
