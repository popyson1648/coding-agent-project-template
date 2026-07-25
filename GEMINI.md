# Repository Rules

## Required Files

This repository must contain:

- `.plans/`
- `.decisions/`
- `.project/`
- `.template/`
- `.project/verification.toml`
- `scripts/verify.py`
- `.pre-commit-config.yaml`
- `.github/workflows/ci.yml`

## Templates

Use the files under `.template/` when creating or refreshing project documentation and config files.

## Subagent Delegation

- When the environment supports subagents, the main agent may proactively delegate self-contained
  research, repository exploration, comparisons, independent review, or high-output verification
  when delegation provides a material context, specialization, or latency benefit.
- Keep small, tightly coupled work and work requiring frequent shared-context decisions in the main
  agent.
- State the objective, bounded scope, expected output and evidence, available tools and sources,
  allowed actions and authority limits, prohibited actions, and dependencies in every delegation.
- Delegation never expands the authority granted to the main agent. A subagent's allowed actions
  must remain within the current task and be a subset of the main agent's authority.
- Default research and review to read-only access. Give an editing subagent ownership of only an
  explicitly bounded area.
- Run tasks in parallel only when they have no unresolved dependency and cannot conflict through
  files, branches, generated artifacts, or external state. Use isolated workspaces or explicit
  non-overlapping ownership for parallel edits.
- Treat subagent output as evidence to inspect. The main agent owns conflict resolution, change
  integration, post-integration verification, final judgment, and the user-facing report.
- Never delegate merge, deployment, or irreversible external actions to a subagent.
- Do not require subagents when the environment lacks them or delegation would add more coordination
  cost than value.

## Document Rules

- Write files under `.project/` in English.
- Write for new contributors and coding agents.
- Keep the documents short and concrete.
- Store decision history in `.decisions/`.
- Store task plans in `.plans/`.
- In a repository with multiple components, mirror component names as subdirectories under `.plans/`, `.decisions/`, and `.project/`; keep single-component repositories flat.

## Plan Rules

- Create one Markdown file per task under `.plans/`.
- Use `.plans/TEMPLATE.md` as the starting point.
- Name plan files `issue-{N}-{slug}.md` for issue-driven work, otherwise `{slug}.md`.
- Keep the `Status` section current: `draft`, `approved`, `in-progress`, `done`, or `abandoned`.
- Track step completion in the `Progress` section with `[ ]`, `[~]`, and `[x]`.

## Decision Rules

- Create one Markdown file per decision under `.decisions/`.
- Record design, rule, structure, and policy decisions.
- Use `.decisions/TEMPLATE.md` as the starting point.
- Name decision files with a short noun-phrase slug: `{slug}.md`.
- Link related issues, pull requests, and superseding or superseded decisions in the `Related` section.
- When a decision replaces an older one, set the old record's `Status` to `superseded` and link both records.

## Project Documentation Rules

- Keep `.project/` focused on the current project state.
- Update `.project/` when commands, workflows, structure, or rules change.
- Use the files under `.template/` as the source templates for `.project/`.

## Verification Rules

- Keep `.project/verification.toml` up to date with the current verification commands.
- Run verification with `python3 scripts/verify.py`.
- Do not assume execute permission on `scripts/verify.py`.

## Local Checks

- Keep `.pre-commit-config.yaml` aligned with the current local verification workflow.

## CI Rules

- Keep `.github/workflows/ci.yml` aligned with the current CI verification workflow.
