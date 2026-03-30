# Conventions

## Naming

- Package code lives under `src/gentms`.
- Annual workbooks use `YYYY年度(RN).xlsx`.
- Monthly workbooks use `YYYY-MM.xlsx` with the resolved calendar year.

## Code Style

- Keep modules small and purpose-specific.
- Prefer explicit functions over hidden side effects.
- Keep workbook schema constants close to the generation code that uses them.

## Review Expectations

- Changes must include tests for any altered CLI, fiscal-year, or workbook behavior.
- Changes that affect signatures or data flow must keep `mypy` passing.
- Changes to output naming or workbook schema must update `.project/` documentation.

## Forbidden Patterns

- Do not silently overwrite existing files or directories.
- Do not change fiscal month ordering from April to March.
- Do not add unsupported leave values without updating validation rules and tests.
