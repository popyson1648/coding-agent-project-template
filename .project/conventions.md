# Conventions

## Naming

- Use short, descriptive task slugs in branch names.
- Prefer `feature/phase{N}-{M}-{slug}` for plan-driven work and `feature/issue-{N}-{slug}` for direct issue work.

## Durable Implementation

- Make each change complete, maintainable, appropriately tested, and consistent with the codebase for its current known requirements.
- Do not knowingly ship an avoidable deficiency on the assumption that it will be repaired later.
- Use clear names, cohesive responsibilities, explicit interfaces, and existing project patterns.
- Choose the simplest design that satisfies current requirements; do not add abstractions, extension points, or functionality for hypothetical future needs.
- Document material tradeoffs. If a constraint makes debt unavoidable, record its reason, scope, impact, and follow-up or revisit condition in a tracked task or decision.
- Treat refactoring required by genuinely new requirements as normal evolution, not proof that the earlier implementation failed this standard.

## Test Timing

- Write or update tests in the same chunk as the change they cover; a change that needs tests is not complete, and is not merged, without them.
- Choose the technique per task instead of fixing one methodology:
  - test-first (TDD) fits when the expected inputs and outputs are clear up front; state that intent explicitly so implementation is not faked against unwritten tests
  - writing tests alongside or immediately after the code fits when the design is still being discovered
- Start a bug fix with a failing test that reproduces the bug whenever the test harness can express it, and keep that test after the fix.
- Deferring tests to a later chunk requires the same recorded approval as any other known deficiency under Durable Implementation.

## Code Style

- Keep project documents short, concrete, and written for new contributors and coding agents.
- Keep plans, implementation, verification, and project docs consistent with each other when a workflow changes.

## Evidence and Research

- Inspect the repository and current environment before relying on external assumptions.
- Before a material proposal, decision, or implementation depends on an uncertain, externally defined, or version-dependent fact, search the web and verify it.
- Prefer current official documentation, specifications, standards, upstream source, and upstream release notes. Use secondary sources only when primary evidence is unavailable, and state that limitation.
- Increase the depth and independence of corroboration with the impact and uncertainty of the decision.
- Cite the evidence used and separate verified facts from inferences, proposals, and unresolved uncertainty.
- Do not put secrets, credentials, private source, or other sensitive data in search queries.
- Web research is optional for stable self-evident facts and facts established directly from the local repository or environment.

## Current State First

- Before proposing, deciding, or acting, inspect the current state that can be checked: the working tree, configuration, documentation, the issue tracker, and any external service involved.
- Report checked facts, inferences, and proposals as clearly separated things, and label any unverified assumption as unverified.
- While the user is consulting, asking, or thinking out loud, do not create issues, post to external services, change files, or change settings without the user's confirmation.
- When such a change looks necessary, present the intended approach or draft first and get confirmation.

## Subagent Delegation

- Delegate proactively only when the environment supports it and the work is self-contained enough
  to return a checkable result. Good candidates include research, repository exploration,
  comparisons, independent review, log inspection, and high-output verification.
- Keep small changes, tightly coupled phases, and work needing frequent shared-context decisions in
  the main agent.
- Give every subagent a delegation brief containing the objective, bounded scope, expected output
  and evidence, available tools and sources, allowed actions and authority limits, prohibited
  actions, and dependencies.
- Delegation cannot expand the authority granted to the main agent. Keep every allowed action within
  the current task and within the main agent's authority.
- Default research and review to read-only access. Limit editing work to an explicitly owned area.
- Parallelize only tasks with no unresolved dependency and no possible conflict through files,
  branches, generated artifacts, or external state. Isolate parallel edits or assign explicit
  non-overlapping ownership.
- The main agent must inspect returned evidence, resolve disagreements, integrate changes, rerun
  verification after integration, make the final decision, and report the result.
- Never delegate merge, deployment, or irreversible external actions. Do not use a subagent when
  coordination cost outweighs the expected benefit.

## Scoped Suggestions

- Make an unrequested suggestion only when it clearly relates to the current work and most of the following hold:
  - the current work measurably increases risk or operating burden
  - deferring it carries a high rework cost
  - the confirmation or setup cost is proportionate to the safety or maintainability gained
  - no equivalent measure already exists, and that has been checked
- Separate suggestions to act on now from suggestions that can wait, and mention the latter briefly instead of expanding them.
- Judge from risk, rework cost, and confirmation cost; do not grow these rules into a trigger table or a per-task checklist.

### Dependency Risk

- Suggest reviewing dependency alerts and Dependabot when dependency risk grows: a package manager or lockfile is introduced, a dependency manifest is added, dependencies increase substantially, or a dependency with a large vulnerability impact arrives.
- Check the current configuration before suggesting: repository Settings > Advanced Security (or the GitHub API) and whether `.github/dependabot.yml` exists.
- Keep the three features distinct: Dependabot alerts (Settings; vulnerability notifications), Dependabot security updates (Settings; automatic fix PRs), and Dependabot version updates (`.github/dependabot.yml`; freshness PRs). All of them are usable for production code.
- Propose version updates or auto-merge only after confirming the user's operating policy.

## Review Expectations

- When a user asks to implement from an approved plan without naming a phase or step range, pick exactly one reviewable chunk:
  - find the next incomplete phase in `Progress`
  - weigh steps by complexity, touched files, and verification cost
  - group only the work needed for one self-contained chunk
- Stop for clarification only when the selected step must be split again because it grew beyond one reviewable chunk, or when the chunk depends on an unmet external prerequisite.
- Treat one request as one chunk, one branch, and one PR unless the user explicitly asks for a different grouping.
- Update `Progress` with `[ ]` before work starts, `[~]` while the selected chunk is in progress, and `[x]` only after verification passes.

## Web UI Verification

- Use Chrome DevTools through the `chrome-devtools-mcp` MCP server as the default way to verify, debug, and optimize anything that runs in a browser; do not judge web UI changes from code alone.
- Use the full toolset, choosing what the change calls for, not only screenshots:
  - rendering and interaction: page navigation, input automation, screenshots
  - runtime errors: console messages and script evaluation
  - API traffic: network request inspection
  - performance: performance traces and their insights
  - release quality: Lighthouse audits as a quality gate
  - device-specific behavior: device, network-speed, and CPU-throttling emulation
  - memory leaks: heap snapshots
- Setup is per environment: register `npx chrome-devtools-mcp@latest` as an MCP server (Claude Code: `/plugin marketplace add ChromeDevTools/chrome-devtools-mcp`, then `/plugin install chrome-devtools-mcp@chrome-devtools-plugins`). Requires Node.js LTS and Chrome.
- If no browser or MCP server is available in the environment, state that limitation and use the closest available verification instead of silently skipping UI verification.

## PR Handling

- After opening a PR, use `gh` for GitHub operations and wait for configured bot feedback before deciding whether more changes are needed.
- If a bot asks for another review pass, reply with the required mention and wait for the follow-up response before merging.
- Keep any repository-specific bot list under the PR handling section and include only bots that are materially active in the current workflow, with what they do and how to mention them.
- At a major stopping point, such as finishing all planned work on a branch, tell the user to clear context before the next large task.

## Troubleshooting

- Start from the observed problem, not from a guessed cause: capture the exact error message, the expected behavior, the actual behavior, and the reproduction conditions.
- When the problem is actively disrupting users or work, stabilize first, then look for the cause.
- Consult sources in order of reliability: the exact error message and logs, official documentation, the upstream issue tracker and known bugs, release notes and changelogs, local configuration and version differences, and recent changes to the repository or environment.
- Form explicit hypotheses and test them one at a time against observations; prefer the simplest explanation that fits all the facts, and treat recent changes as prime suspects.
- Keep observed facts, tested results, and untested hypotheses separated. Investigation alone does not confirm a cause; a cause is confirmed when it reproduces the problem or makes it appear and disappear predictably.
- Watch for the standard traps: correlation is not causation, and "the same as last time" is a hypothesis, not a conclusion.
- Use unverified blog posts and anecdotes only as leads, and confirm them against primary sources before relying on them.
- Scale investigation depth to the impact of the problem; small problems do not require long external research. Any web research follows the Evidence and Research rules.

## Fix and Verification Integrity

- Reproduce and investigate a warning, error, or failing check before changing code or tool configuration.
- Fix the underlying cause, then rerun the original failing check and the relevant verification suite.
- Do not disable checks, add broad ignores, lower severity, comment out tests, weaken assertions, or alter expected output solely to obtain a passing result.
- Allow a suppression only when evidence confirms a false positive, upstream tool defect, unavoidable compatibility constraint, or explicitly accepted risk and no practical direct fix is available.
- Keep an allowed exception to the smallest practical scope, explain the reason next to it, preserve relevant coverage, and record a removal condition or tracked follow-up when temporary.
- Require recorded user or maintainer approval before accepting a material unresolved risk.
- Report any warning, failure, or uncertainty that remains after verification.

## Forbidden Patterns

- Do not create GitHub issues or other external artifacts that the user did not ask for.
- Do not implement multiple chunks on the same branch by default.
- Do not skip the `[~]` state when work has started but is not yet complete.
- Do not merge immediately after opening a PR without checking for bot feedback.
- Do not list inactive or irrelevant bots in PR handling guidance.
- Do not use web UI steps when the same GitHub operation can be done with `gh`.
