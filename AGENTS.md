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

## Autonomous Execution Loop

- For the current approved reviewable chunk of an implementation or repair task, autonomously repeat
  investigate and plan, act, verify, and adapt until a completion or stop condition is reached. Do
  not require the user to invoke a product-specific loop command.
- Before the first implementation action, record observable success criteria, required verification,
  stop conditions, approval boundaries, and task-specific resource or iteration limits in the task
  plan.
- A finite total-cycle limit is mandatory. When the plan does not set another finite limit, allow at
  most eight cycles for the current chunk. Record stricter time, context, or cost limits when the
  environment exposes them.
- Use the task's `.plans/` file as durable state across turns, context compaction, handoffs, and
  agent products. Keep its `Status`, `Progress`, `Loop State`, and `Verification` evidence current at
  each meaningful verification cycle and before a handoff.
- In each cycle:
  1. Inspect the current plan, repository and external state, and the latest verification evidence.
  2. Choose the smallest action that can produce new evidence toward an unmet success criterion.
  3. Act only within the approved scope and authority.
  4. Run the narrowest relevant check, then the configured broader verification when warranted.
  5. Record the observation, update progress, and select the next action from the evidence.
- After a failed check, diagnose the result and change the hypothesis, implementation, or test. Do
  not repeat the same action against materially unchanged state. One documented repeat is allowed
  only to test a plausible transient or flaky failure.
- Continue only while the loop remains within authority and limits. Count a cycle as measurable
  progress when it satisfies a criterion, reproduces or narrows a failure, supports or rejects a
  stated hypothesis, or identifies required external input. If the plan has no stricter limit, stop
  after two consecutive cycles without measurable progress, or immediately when no materially
  different evidence-backed next action is available.
- Do not change scope, success criteria, required verification, or accepted risk merely to let the
  loop continue or pass. Do not disable checks, weaken assertions, broaden suppressions, or change
  expected results without evidence that the verification is wrong and the exception rules are met.
- After the first implementation action, do not raise, remove, or reset a cycle, no-progress, time,
  context, or cost limit without explicit user or maintainer approval for a new finite limit.
- Treat `scripts/verify.py` as evidence only for the relevant phases it actually runs. If required
  behavior has no enabled coverage, run an appropriate additional check or stop and report the
  verification gap.
- Mark work complete only when every success criterion is supported by evidence on the integrated
  state, all required verification has run and passed, and final review finds no unresolved material
  concern except a risk explicitly accepted by the user or maintainer under the existing approval
  rules. A final response, plan checkbox, subagent report, or successful worker exit is not
  completion evidence by itself.
- Stop and report instead of continuing when success is reached; an approval or permission boundary
  is reached; requirements conflict; a required external dependency or tool is unavailable; safety
  or security is uncertain; verification cannot establish success; a resource limit is reached; or
  the no-progress limit is reached.
- On a non-success stop, keep the task and current step non-done and record the stop reason, last
  evidence, attempted distinct approaches, and recommended next action. Ask the user only for the
  specific decision or authority needed to resume; do not mark the plan `done` or `abandoned` unless
  its lifecycle actually ended.
- The loop never expands the user's authorization and never implies permission for external writes
  such as issue or PR changes, messages, or pushes; destructive or irreversible actions; secret or
  credential access; purchases; merge, deploy, or publish; weakening checks; or accepting material
  risk.
- Subagent delegation does not reset loop limits or transfer integration, reverification, stopping,
  or completion judgment away from the main agent.
- Product-native loops, goals, hooks, schedulers, checkpoints, worktrees, and subagents may
  accelerate this contract but are optional. The portable core is repository instructions, durable
  plan state, and executable project verification.

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
