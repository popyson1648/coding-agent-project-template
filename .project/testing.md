# Testing

## Test Types

## Minimum Checks Before Completion

## Checks By Change Type

## How To Run Verification

## Secrets Scanning

- Recommended tool: gitleaks. It is language- and framework-independent and works in both pre-commit and CI.
- Set it up as soon as the repository holds real code or configuration:
  1. Install gitleaks (Homebrew, release binary, or the `ghcr.io/gitleaks/gitleaks` image).
  2. Enable `[phases.secrets]` in `.project/verification.toml` with a command such as `gitleaks git --no-banner .`.
  3. Both pre-commit and CI already run `python3 scripts/verify.py`, so the phase runs in both without extra wiring.
- Create `.gitleaks.toml` at the repository root only when custom rules or allowlists are needed; gitleaks picks it up automatically.
- Treat `.gitleaksignore` entries and `gitleaks:allow` comments as suppressions: they need evidence and a reason, following the fix and verification integrity rules in `.project/conventions.md`.
