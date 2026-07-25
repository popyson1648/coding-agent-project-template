# Testing

## Test Types

## Minimum Checks Before Completion

## Checks By Change Type

## How To Run Verification

### Full verification

- Run `python3 scripts/verify.py` locally and before completion. With no event option, every enabled
  phase runs.
- Use `python3 scripts/verify.py --event full` when an explicit event name is useful.

### Impact-based verification

- Schema version 2 declares repository-relative path scopes under `[inputs.<name>]`.
- Set `depends_on` when a change to one input can affect another input. A phase references the
  resulting scopes with `inputs`.
- Set each phase's `when` list to `["always"]`, or combine `changed`, `scheduled`, and `manual`.
- Keep `[selection].selector_paths` for selection definitions and `global_paths` for shared files
  whose changes require every eligible phase.
- A named input referenced by no phase marks a known unrelated change. A path matching no input is
  unknown and forces full fallback.
- Run `python3 scripts/verify.py --event changed --base <base-sha> --head <head-sha>` for a Git
  comparison, or repeat `--changed-file <repository-relative-path>` when the caller already knows
  the changed paths.
- Run scheduled or human-requested phase policies with `--event scheduled` or `--event manual`.
- Unknown paths, selector or global changes, and unavailable Git comparison data deliberately fall
  back to all eligible phases.
- The shipped `[inputs.repository]` table uses `paths = ["**"]` as a safe broad default. Split it
  into narrower named inputs only when the repository's path ownership and dependency relationships
  are known.
- CI keeps the required workflow and job active, then selects affected phases inside `verify.py`.
  Pre-commit and plain manual invocation remain full verification.

## Secrets Scanning

- Recommended tool: gitleaks. It is language- and framework-independent and works in both pre-commit and CI.
- Set it up as soon as the repository holds real code or configuration:
  1. Install gitleaks (Homebrew, release binary, or the `ghcr.io/gitleaks/gitleaks` image).
  2. Enable `[phases.secrets]` in `.project/verification.toml` with a command such as `gitleaks git --no-banner .`.
  3. Pre-commit and CI already invoke `verify.py`, so the phase runs in both without extra wiring.
- Create `.gitleaks.toml` at the repository root only when custom rules or allowlists are needed; gitleaks picks it up automatically.
- Treat `.gitleaksignore` entries and `gitleaks:allow` comments as suppressions: they need evidence and a reason, following the fix and verification integrity rules in `.project/conventions.md`.
