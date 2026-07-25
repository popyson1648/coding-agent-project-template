# Coding Agent Project Template

**English** | [日本語](README.ja.md)

[![CI](https://img.shields.io/github/actions/workflow/status/popyson1648/coding-agent-project-template/ci.yml?branch=main&label=CI)](https://github.com/popyson1648/coding-agent-project-template/actions/workflows/ci.yml)
[![Latest Release](https://img.shields.io/github/v/release/popyson1648/coding-agent-project-template?label=release)](https://github.com/popyson1648/coding-agent-project-template/releases)
[![License](https://img.shields.io/github/license/popyson1648/coding-agent-project-template?label=license)](LICENSE)

A project harness for working with coding agents (Claude Code, Gemini CLI, Codex, and similar).
It ships shared agent rules, a plan and decision log, project documentation skeletons, and a single
verification entry point wired into pre-commit and CI.

After adopting the template, replace this README with your project's own README.

## Table of Contents

- [What You Get](#what-you-get)
- [Start a New Project](#start-a-new-project)
- [Configure Verification](#configure-verification)
- [Adopt Into an Existing Project](#adopt-into-an-existing-project)
- [Update From the Template](#update-from-the-template)
- [Requirements](#requirements)
- [License](#license)

## What You Get

- `AGENTS.md` / `CLAUDE.md` / `GEMINI.md`: repository rules that agents load; kept identical.
- `.plans/`: one Markdown plan per task (`.plans/TEMPLATE.md`).
- `.decisions/`: one Markdown record per decision (`.decisions/TEMPLATE.md`).
- `.project/`: current project documentation (conventions, structure, build, testing, release).
- `.template/`: source templates for the `.project/` files and for the config files.
- `scripts/verify.py`: runs the verification phases defined in `.project/verification.toml`.
- `.pre-commit-config.yaml`, `.github/workflows/ci.yml`, and `.github/dependabot.yml`: local
  verification, CI verification, and GitHub Actions update checks.
- `.gitignore`: baseline Python, OS, and editor ignores; extend it for your project's language and
  tools.

## Start a New Project

1. Click **Use this template** on GitHub and create the repository.
2. Fill in the `.project/` documents from the skeletons in `.template/`.
3. Enable verification phases in `.project/verification.toml` as you add real tooling.
4. Install the local hook: `pre-commit install`.

## Configure Verification

`python3 scripts/verify.py` remains the full-verification command for local work and completion
checks. CI keeps the workflow and job running, then passes `--event changed` with the push or
pull-request base/head SHAs so the runner can select affected phases.

Schema version 2 adds three pieces of impact metadata:

- `[inputs.<name>]` maps repository-relative path patterns to a named input. `depends_on` declares
  which other inputs can affect it.
- A phase's `inputs` selects its scopes. Set `when` to `["always"]`, or combine `changed`,
  `scheduled`, and `manual`.
- `[selection].selector_paths` identifies selection definitions, and `global_paths` identifies
  shared files whose changes require every eligible phase.

The template starts with one broad `repository` input matching `**`. This intentionally runs every
enabled phase for every known change until the project has an accurate path and dependency map.
Unknown paths, selector or global changes, and unavailable Git comparison data also fall back to all
eligible phases.

```bash
# Full verification
python3 scripts/verify.py

# Compare two Git revisions
python3 scripts/verify.py --event changed --base <base-sha> --head <head-sha>

# Supply a changed path directly
python3 scripts/verify.py --event changed --changed-file src/example.py

# Inspect scheduled or manual policies
python3 scripts/verify.py --event scheduled --list
python3 scripts/verify.py --event manual --list
```

The `scheduled` and `manual` values select phase policies; they do not create a scheduler or a
manual workflow trigger. See `.project/testing.md` for the configuration contract and fallback
behavior.

## Adopt Into an Existing Project

GitHub's "Use this template" only creates new repositories, so adoption is a file copy.

1. Download the template without git history (any equivalent download works; the `npx giget`
   example requires Node.js/npm):

   ```bash
   npx giget@latest gh:popyson1648/coding-agent-project-template .tmp/agent-template
   ```

2. From your project root, copy everything that does not exist yet (`-n` never overwrites; recent
   GNU cp prints a portability warning for it and offers `--update=none` as the equivalent):

   ```bash
   cp -Rn .tmp/agent-template/.plans .tmp/agent-template/.decisions \
          .tmp/agent-template/.project .tmp/agent-template/.template .
   cp -n .tmp/agent-template/AGENTS.md .tmp/agent-template/CLAUDE.md \
         .tmp/agent-template/GEMINI.md .tmp/agent-template/.pre-commit-config.yaml .
   mkdir -p scripts .github/workflows
   cp -n .tmp/agent-template/scripts/verify.py scripts/
   cp -n .tmp/agent-template/.github/workflows/ci.yml .github/workflows/
   cp -n .tmp/agent-template/.github/dependabot.yml .github/
   ```

3. Reconcile by hand anything that already existed: merge the template's rules into your existing
   `AGENTS.md`/`CLAUDE.md`/`GEMINI.md` (keep the three identical), and merge the verification step
   into your existing pre-commit and CI configs. Keep pre-commit on plain full verification and pass
   `--mode ci --event changed` with explicit base/head SHAs from CI.
4. Fill in the `.project/` documents from `.template/` and put your real commands into
   `.project/verification.toml` (phases start disabled so CI stays green until you enable them).
5. Verify and clean up:

   ```bash
   python3 scripts/verify.py
   pre-commit install
   rm -rf .tmp/agent-template
   ```

## Update From the Template

Every published change to this template also refreshes `.template-version` (the source commit,
publish date, and release tag) and cuts a dated [GitHub Release](https://github.com/popyson1648/coding-agent-project-template/releases)
with auto-generated notes. Check the release badge above or the Releases page for a human-readable
version; `.template-version` is the machine-readable equivalent. Never edit either by hand.

### Recommended: merge from the template remote

This works whether the project was created with "Use this template" or adopted by file copy.

```bash
git remote add template https://github.com/popyson1648/coding-agent-project-template.git
git fetch template
git merge template/main --allow-unrelated-histories   # first sync only
```

Every later sync is an ordinary three-way merge:

```bash
git fetch template && git merge template/main
```

- Git records the merge base, so your local customizations survive and conflicts appear only where
  both sides changed the same lines. Resolve them, run `python3 scripts/verify.py`, then commit.
- Do not squash template merges: squashing discards the merge base, and every future sync conflicts
  from scratch.

### Alternative: apply the template diff without adding a remote

If the project has a `.template-version`, you can apply only the template's old-to-new diff:

```bash
git clone https://github.com/popyson1648/coding-agent-project-template .tmp/template
BASE=$(git -C .tmp/template log --format=%H \
  --grep "$(sed -n 's/^source-commit: //p' .template-version)")
git -C .tmp/template diff "$BASE"..HEAD | git apply --reject
rm -rf .tmp/template
```

Resolve any `.rej` files by hand (the diff also refreshes `.template-version`), run
`python3 scripts/verify.py`, then commit. Prefer the merge path when possible; a real three-way
merge resolves more cases than a blind patch.

Projects adopted before `.template-version` existed should use the merge path; its first
`--allow-unrelated-histories` sync establishes the merge base.

For scheduled, automated update PRs, see the third-party
[actions-template-sync](https://github.com/AndreasAugustin/actions-template-sync) action (needs its
own token setup per project).

## Requirements

- Python 3.11+ (for `scripts/verify.py`)
- [pre-commit](https://pre-commit.com/) for the local hook
- Node.js/npm only when using the `npx giget` adoption command shown above

## License

This template is licensed under the [Mozilla Public License 2.0](LICENSE).
