# Release

## When Release Is Needed

A release is needed when the CLI behavior, workbook schema, or installation workflow changes in a way that users must consume explicitly.

## Release Steps

- Run `python3 scripts/verify.py`.
- Confirm `.project/` documents describe the current commands and checks.
- Confirm the decision and plan records are up to date.

## Required Checks

- `python3 scripts/verify.py`

## Rollback Or Recovery Notes

If a change breaks workbook output, revert the affected branch commit and regenerate sample workbooks to confirm the previous behavior.
