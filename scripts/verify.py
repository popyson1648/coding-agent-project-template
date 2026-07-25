#!/usr/bin/env python3

from __future__ import annotations

import argparse
import fnmatch
import os
import subprocess
import sys
from pathlib import Path
import tomllib


DEFAULT_ORDER = [
    "secrets",
    "format",
    "lint",
    "typecheck",
    "build",
    "test_unit",
    "test_integration",
    "test_e2e",
    "test_component",
    "test_contract",
    "accessibility",
    "performance",
    "bundle_size",
]

MODE_FLAG_MAP = {
    "all": None,
    "edit": "run_on_edit",
    "pre-commit": "run_pre_commit",
    "pre-push": "run_pre_push",
    "ci": "run_in_ci",
}

EVENT_NAMES = ("always", "changed", "scheduled", "manual")
PHASE_COMMON_KEYS = {
    "enabled",
    "command",
    "reason",
    "run_on_edit",
    "run_pre_commit",
    "run_pre_push",
    "run_in_ci",
}
PHASE_V2_KEYS = PHASE_COMMON_KEYS | {"inputs", "when"}
TOP_LEVEL_V2_KEYS = {"version", "selection", "inputs", "phases"}
SELECTION_KEYS = {"selector_paths", "global_paths"}
INPUT_KEYS = {"paths", "depends_on"}


def _config_error(message: str) -> None:
    print(message, file=sys.stderr)
    raise SystemExit(2)


def load_config(config_path: Path) -> dict:
    if not config_path.exists():
        _config_error(f"verification config not found: {config_path}")

    try:
        with config_path.open("rb") as f:
            data = tomllib.load(f)
    except tomllib.TOMLDecodeError as error:
        _config_error(f"invalid verification config: {error}")

    if not isinstance(data, dict):
        _config_error("verification config must be a TOML table")

    return data


def normalize_phase(name: str, entry: dict) -> dict:
    """Normalize a version 1 phase while preserving the original permissive rules."""
    if not isinstance(entry, dict):
        _config_error(f"phase '{name}' must be a TOML table")

    return {
        "name": name,
        "enabled": bool(entry.get("enabled", False)),
        "command": str(entry.get("command", "")).strip(),
        "reason": str(entry.get("reason", "")).strip(),
        "run_on_edit": _optional_bool(entry.get("run_on_edit")),
        "run_pre_commit": _optional_bool(entry.get("run_pre_commit")),
        "run_pre_push": _optional_bool(entry.get("run_pre_push")),
        "run_in_ci": _optional_bool(entry.get("run_in_ci")),
        "inputs": [],
        "when": ["always"],
    }


def _optional_bool(value: object) -> bool | None:
    if value is None:
        return None
    return bool(value)


def _strict_optional_bool(entry: dict, key: str, context: str) -> bool | None:
    value = entry.get(key)
    if value is None:
        return None
    if not isinstance(value, bool):
        _config_error(f"{context}.{key} must be a boolean")
    return value


def _strict_string(entry: dict, key: str, context: str) -> str:
    value = entry.get(key, "")
    if not isinstance(value, str):
        _config_error(f"{context}.{key} must be a string")
    return value.strip()


def _strict_string_list(
    value: object,
    context: str,
    *,
    allow_empty: bool = True,
) -> list[str]:
    if not isinstance(value, list) or any(not isinstance(item, str) for item in value):
        _config_error(f"{context} must be an array of strings")
    if not allow_empty and not value:
        _config_error(f"{context} must not be empty")
    if any(not item for item in value):
        _config_error(f"{context} must not contain empty strings")
    if len(set(value)) != len(value):
        _config_error(f"{context} must not contain duplicate values")
    return list(value)


def _ordered_phases(phases_by_name: dict[str, dict]) -> list[dict]:
    remaining = dict(phases_by_name)
    ordered: list[dict] = []

    for name in DEFAULT_ORDER:
        phase = remaining.pop(name, None)
        if phase is not None:
            ordered.append(phase)

    for name in sorted(remaining):
        ordered.append(remaining[name])

    return ordered


def collect_phases(config: dict) -> list[dict]:
    raw_phases = config.get("phases")
    if raw_phases is None:
        return []

    if not isinstance(raw_phases, dict):
        _config_error("[phases] must be a TOML table")

    return _ordered_phases(
        {name: normalize_phase(name, entry) for name, entry in raw_phases.items()}
    )


def validate_path_pattern(pattern: str, context: str = "path pattern") -> str:
    if not isinstance(pattern, str) or not pattern:
        _config_error(f"{context} must be a non-empty string")
    if pattern.startswith("!"):
        _config_error(f"{context} must not be a negative pattern: {pattern!r}")
    if pattern.startswith("/"):
        _config_error(f"{context} must be repository-relative: {pattern!r}")
    if "\\" in pattern:
        _config_error(f"{context} must use '/' separators: {pattern!r}")

    segments = pattern.split("/")
    if any(segment in {"", ".", ".."} for segment in segments):
        _config_error(f"{context} contains an invalid path segment: {pattern!r}")
    if any("**" in segment and segment != "**" for segment in segments):
        _config_error(
            f"{context} may use '**' only as a complete path segment: {pattern!r}"
        )
    for segment in segments:
        index = 0
        while index < len(segment):
            if segment[index] != "[":
                index += 1
                continue
            closing = index + 1
            if closing < len(segment) and segment[closing] in {"!", "^"}:
                closing += 1
            if closing < len(segment) and segment[closing] == "]":
                closing += 1
            closing = segment.find("]", closing)
            if closing < 0:
                _config_error(
                    f"{context} has an unclosed character class: {pattern!r}"
                )
            index = closing + 1
    return pattern


def _normalize_changed_path(path: str) -> str | None:
    if (
        not isinstance(path, str)
        or not path
        or "\0" in path
        or path.startswith("/")
        or "\\" in path
    ):
        return None
    segments = path.split("/")
    if any(segment in {"", ".", ".."} for segment in segments):
        return None
    return path


def matches_path(path: str, pattern: str) -> bool:
    """Return whether a repository-relative POSIX path wholly matches a glob."""
    if _normalize_changed_path(path) is None:
        return False

    validate_path_pattern(pattern)
    pattern_segments = pattern.split("/")

    path_segments = path.split("/")
    memo: dict[tuple[int, int], bool] = {}

    def match(path_index: int, pattern_index: int) -> bool:
        key = (path_index, pattern_index)
        if key in memo:
            return memo[key]

        if pattern_index == len(pattern_segments):
            result = path_index == len(path_segments)
        elif pattern_segments[pattern_index] == "**":
            result = match(path_index, pattern_index + 1) or (
                path_index < len(path_segments)
                and match(path_index + 1, pattern_index)
            )
        else:
            result = (
                path_index < len(path_segments)
                and fnmatch.fnmatchcase(
                    path_segments[path_index],
                    pattern_segments[pattern_index],
                )
                and match(path_index + 1, pattern_index + 1)
            )

        memo[key] = result
        return result

    return match(0, 0)


def _normalized_repo_path(path: Path | str | None) -> str | None:
    if path is None:
        return None
    candidate = Path(path)
    try:
        if candidate.is_absolute():
            candidate = candidate.relative_to(Path.cwd())
        candidate = Path(os.path.normpath(candidate.as_posix()))
        return _normalize_changed_path(candidate.as_posix())
    except ValueError:
        return None


def _validate_version(config: dict) -> int:
    version = config.get("version", 1)
    if isinstance(version, bool) or not isinstance(version, int):
        _config_error("version must be an integer")
    if version not in {1, 2}:
        _config_error(f"unsupported verification config version: {version}")
    return version


def _validate_v2_phase(name: str, entry: object, input_names: set[str]) -> dict:
    context = f"phases.{name}"
    if not isinstance(entry, dict):
        _config_error(f"phase '{name}' must be a TOML table")
    unknown = sorted(set(entry) - PHASE_V2_KEYS)
    if unknown:
        _config_error(f"[{context}] has unknown keys: {', '.join(unknown)}")

    enabled = entry.get("enabled", False)
    if not isinstance(enabled, bool):
        _config_error(f"{context}.enabled must be a boolean")

    inputs = _strict_string_list(entry.get("inputs", []), f"{context}.inputs")
    missing_inputs = sorted(set(inputs) - input_names)
    if missing_inputs:
        _config_error(
            f"{context}.inputs references unknown inputs: {', '.join(missing_inputs)}"
        )

    when = _strict_string_list(
        entry.get("when", ["always"]),
        f"{context}.when",
        allow_empty=False,
    )
    unknown_events = sorted(set(when) - set(EVENT_NAMES))
    if unknown_events:
        _config_error(
            f"{context}.when has unknown events: {', '.join(unknown_events)}"
        )
    if "always" in when and len(when) != 1:
        _config_error(f"{context}.when must not combine always with other events")
    if "changed" in when and not inputs:
        _config_error(f"{context}.when includes changed but inputs is empty")

    return {
        "name": name,
        "enabled": enabled,
        "command": _strict_string(entry, "command", context),
        "reason": _strict_string(entry, "reason", context),
        "run_on_edit": _strict_optional_bool(entry, "run_on_edit", context),
        "run_pre_commit": _strict_optional_bool(entry, "run_pre_commit", context),
        "run_pre_push": _strict_optional_bool(entry, "run_pre_push", context),
        "run_in_ci": _strict_optional_bool(entry, "run_in_ci", context),
        "inputs": inputs,
        "when": when,
    }


def _reject_input_cycles(inputs: dict[str, dict]) -> None:
    state: dict[str, int] = {}
    stack: list[str] = []

    def visit(name: str) -> None:
        current = state.get(name, 0)
        if current == 2:
            return
        if current == 1:
            cycle_start = stack.index(name)
            cycle = stack[cycle_start:] + [name]
            _config_error(f"input dependency cycle: {' -> '.join(cycle)}")

        state[name] = 1
        stack.append(name)
        for dependency in inputs[name]["depends_on"]:
            visit(dependency)
        stack.pop()
        state[name] = 2

    for name in sorted(inputs):
        visit(name)


def validate_config(config: dict, config_path: Path | str | None = None) -> dict:
    """Validate and normalize either the compatible v1 or strict v2 schema."""
    if not isinstance(config, dict):
        _config_error("verification config must be a TOML table")

    version = _validate_version(config)
    if version == 1:
        normalized = {
            "version": 1,
            "selection": {
                "selector_paths": ["scripts/verify.py"],
                "global_paths": [],
            },
            "inputs": {},
            "phases": collect_phases(config),
        }
        normalized_config_path = _normalized_repo_path(config_path)
        if normalized_config_path is not None:
            normalized["selection"]["selector_paths"].append(normalized_config_path)
        return normalized

    unknown = sorted(set(config) - TOP_LEVEL_V2_KEYS)
    if unknown:
        _config_error(f"verification config has unknown keys: {', '.join(unknown)}")

    raw_selection = config.get("selection", {})
    if not isinstance(raw_selection, dict):
        _config_error("[selection] must be a TOML table")
    unknown_selection = sorted(set(raw_selection) - SELECTION_KEYS)
    if unknown_selection:
        _config_error(
            f"[selection] has unknown keys: {', '.join(unknown_selection)}"
        )

    selection: dict[str, list[str]] = {}
    for key in sorted(SELECTION_KEYS):
        patterns = _strict_string_list(
            raw_selection.get(key, []),
            f"selection.{key}",
        )
        selection[key] = [
            validate_path_pattern(pattern, f"selection.{key}")
            for pattern in patterns
        ]

    raw_inputs = config.get("inputs", {})
    if not isinstance(raw_inputs, dict):
        _config_error("[inputs] must be a TOML table")

    inputs: dict[str, dict] = {}
    for name, entry in raw_inputs.items():
        context = f"inputs.{name}"
        if not name:
            _config_error("input names must not be empty")
        if not isinstance(entry, dict):
            _config_error(f"[{context}] must be a TOML table")
        unknown_input_keys = sorted(set(entry) - INPUT_KEYS)
        if unknown_input_keys:
            _config_error(f"[{context}] has unknown keys: {', '.join(unknown_input_keys)}")

        paths = _strict_string_list(
            entry.get("paths", []),
            f"{context}.paths",
            allow_empty=False,
        )
        depends_on = _strict_string_list(
            entry.get("depends_on", []),
            f"{context}.depends_on",
        )
        inputs[name] = {
            "name": name,
            "paths": [
                validate_path_pattern(pattern, f"{context}.paths")
                for pattern in paths
            ],
            "depends_on": depends_on,
        }

    input_names = set(inputs)
    for name, entry in inputs.items():
        missing = sorted(set(entry["depends_on"]) - input_names)
        if missing:
            _config_error(
                f"inputs.{name}.depends_on references unknown inputs: {', '.join(missing)}"
            )
        if name in entry["depends_on"]:
            _config_error(f"inputs.{name}.depends_on must not reference itself")
    _reject_input_cycles(inputs)

    raw_phases = config.get("phases", {})
    if not isinstance(raw_phases, dict):
        _config_error("[phases] must be a TOML table")
    phases = _ordered_phases(
        {
            name: _validate_v2_phase(name, entry, input_names)
            for name, entry in raw_phases.items()
        }
    )

    normalized = {
        "version": 2,
        "selection": selection,
        "inputs": inputs,
        "phases": phases,
    }
    if "scripts/verify.py" not in normalized["selection"]["selector_paths"]:
        normalized["selection"]["selector_paths"].append("scripts/verify.py")
    normalized_config_path = _normalized_repo_path(config_path)
    if (
        normalized_config_path is not None
        and normalized_config_path not in normalized["selection"]["selector_paths"]
    ):
        normalized["selection"]["selector_paths"].append(normalized_config_path)
    return normalized


def is_selected_for_mode(phase: dict, mode: str) -> bool:
    if not phase["enabled"]:
        return False

    flag_name = MODE_FLAG_MAP[mode]
    if flag_name is None:
        return True

    flag_value = phase.get(flag_name)
    if flag_value is None:
        return True

    return bool(flag_value)


def run_command(command: str) -> int:
    completed = subprocess.run(command, shell=True)
    return completed.returncode


def collect_changed_files(
    repo_root: Path | str,
    base: str,
    head: str,
) -> tuple[list[str], str | None]:
    """Collect changed paths from one merge-base comparison."""
    root = Path(repo_root)
    if not base or not head or base.startswith("-") or head.startswith("-"):
        return [], "invalid Git base or head"

    try:
        merge_base_result = subprocess.run(
            ["git", "merge-base", "--all", base, head],
            cwd=root,
            check=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
    except OSError:
        return [], "Git is unavailable"

    if merge_base_result.returncode != 0:
        return [], "Git merge-base could not be determined"

    merge_base_lines = merge_base_result.stdout.splitlines()
    if len(merge_base_lines) != 1:
        return [], "Git merge-base returned an indeterminate result"
    try:
        merge_base = merge_base_lines[0].decode("ascii")
    except UnicodeDecodeError:
        return [], "Git merge-base returned an invalid object name"
    if not merge_base:
        return [], "Git merge-base returned an empty object name"

    try:
        diff_result = subprocess.run(
            [
                "git",
                "diff",
                "--name-status",
                "-z",
                "--no-renames",
                merge_base,
                head,
                "--",
            ],
            cwd=root,
            check=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
    except OSError:
        return [], "Git diff is unavailable"
    if diff_result.returncode != 0:
        return [], "Git diff could not be determined"

    fields = diff_result.stdout.split(b"\0")
    if fields and fields[-1] == b"":
        fields.pop()
    if len(fields) % 2:
        return [], "Git diff returned malformed name-status data"

    changed: set[str] = set()
    allowed_statuses = {"A", "D", "M", "T"}
    for index in range(0, len(fields), 2):
        try:
            status = fields[index].decode("ascii")
        except UnicodeDecodeError:
            return [], "Git diff returned an invalid status"
        if status not in allowed_statuses:
            return [], f"Git diff returned unsupported status: {status!r}"

        path = os.fsdecode(fields[index + 1])
        if _normalize_changed_path(path) is None:
            return [], f"Git diff returned an invalid path: {path!r}"
        changed.add(path)

    return sorted(changed), None


def _first_matching_path(
    paths: list[str],
    patterns: list[str],
) -> tuple[str, str] | None:
    for path in paths:
        for pattern in patterns:
            if matches_path(path, pattern):
                return path, pattern
    return None


def collect_affected_inputs(
    normalized_config: dict,
    changed_paths: list[str],
) -> tuple[set[str], str | None, dict[str, str]]:
    """Resolve directly changed inputs and their transitive reverse dependents."""
    paths = sorted(set(changed_paths))
    input_reasons: dict[str, str] = {}
    for path in paths:
        if _normalize_changed_path(path) is None:
            return set(), f"invalid changed path: {path!r}", input_reasons

    selection = normalized_config["selection"]
    selector_match = _first_matching_path(paths, selection["selector_paths"])
    if selector_match is not None:
        path, pattern = selector_match
        return (
            set(),
            f"selector path changed: {path!r} matched {pattern!r}",
            input_reasons,
        )
    global_match = _first_matching_path(paths, selection["global_paths"])
    if global_match is not None:
        path, pattern = global_match
        return (
            set(),
            f"global path changed: {path!r} matched {pattern!r}",
            input_reasons,
        )

    inputs = normalized_config["inputs"]
    directly_affected: set[str] = set()
    for path in paths:
        matched: list[tuple[str, str]] = []
        for name, entry in sorted(inputs.items()):
            for pattern in entry["paths"]:
                if matches_path(path, pattern):
                    matched.append((name, pattern))
                    break
        if not matched:
            return set(), f"unknown changed path: {path!r}", input_reasons
        for name, pattern in matched:
            directly_affected.add(name)
            input_reasons.setdefault(
                name,
                f"changed path {path!r} matched input {name}:{pattern!r}",
            )

    affected = set(directly_affected)
    changed = True
    while changed:
        changed = False
        for name, entry in sorted(inputs.items()):
            if name in affected:
                continue
            dependency = next(
                (
                    dependency
                    for dependency in sorted(entry["depends_on"])
                    if dependency in affected
                ),
                None,
            )
            if dependency is None:
                continue
            affected.add(name)
            input_reasons[name] = (
                f"input {name} depends on affected input {dependency}"
            )
            changed = True

    return affected, None, input_reasons


def _decision(phase: dict, selected: bool, reason: str) -> dict:
    return {
        "name": phase["name"],
        "phase": phase,
        "selected": selected,
        "reason": reason,
    }


def select_for_event(
    normalized_config: dict,
    event: str,
    changed_paths: list[str] | None = None,
    fallback_reason: str | None = None,
) -> list[dict]:
    if event not in {"full", "changed", "scheduled", "manual"}:
        _config_error(f"unknown verification event: {event}")

    phases = normalized_config["phases"]
    affected_inputs: set[str] = set()
    input_reasons: dict[str, str] = {}
    if event == "changed" and fallback_reason is None:
        affected_inputs, impact_fallback, input_reasons = collect_affected_inputs(
            normalized_config,
            changed_paths or [],
        )
        if impact_fallback:
            fallback_reason = impact_fallback

    decisions: list[dict] = []
    for phase in phases:
        if not phase["enabled"]:
            decisions.append(
                _decision(phase, False, phase["reason"] or "phase is disabled")
            )
            continue
        if event == "full":
            decisions.append(_decision(phase, True, "explicit full verification"))
            continue
        if fallback_reason is not None:
            decisions.append(
                _decision(phase, True, f"full fallback: {fallback_reason}")
            )
            continue
        if "always" in phase["when"]:
            decisions.append(_decision(phase, True, "policy always"))
            continue

        if event in {"scheduled", "manual"}:
            selected = event in phase["when"]
            decisions.append(
                _decision(
                    phase,
                    selected,
                    f"policy {event}"
                    if selected
                    else f"event {event} does not match phase policy",
                )
            )
            continue

        if "changed" not in phase["when"]:
            decisions.append(
                _decision(phase, False, "event changed does not match phase policy")
            )
            continue

        matched_input = next(
            (
                input_name
                for input_name in phase["inputs"]
                if input_name in affected_inputs
            ),
            None,
        )
        if matched_input is None:
            decisions.append(_decision(phase, False, "no affected inputs"))
        else:
            decisions.append(
                _decision(phase, True, input_reasons[matched_input])
            )

    return decisions


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run repository verification phases from .project/verification.toml."
    )
    parser.add_argument(
        "--config",
        default=".project/verification.toml",
        help="Path to verification.toml",
    )
    parser.add_argument(
        "--mode",
        choices=["all", "edit", "pre-commit", "pre-push", "ci"],
        default="all",
        help="Execution mode",
    )
    parser.add_argument(
        "--event",
        choices=["full", "changed", "scheduled", "manual"],
        default="full",
        help="Verification-selection event",
    )
    parser.add_argument(
        "--base",
        help="Base Git revision for --event changed",
    )
    parser.add_argument(
        "--head",
        help="Head Git revision for --event changed",
    )
    parser.add_argument(
        "--changed-file",
        action="append",
        default=[],
        help="Repository-relative changed path; may be repeated",
    )
    parser.add_argument(
        "--only",
        nargs="*",
        default=[],
        help="Run only the specified phases",
    )
    parser.add_argument(
        "--list",
        action="store_true",
        help="List selected phases and exit",
    )
    args = parser.parse_args(argv)

    has_git_ref = args.base is not None or args.head is not None
    if has_git_ref and args.changed_file:
        parser.error("--changed-file cannot be combined with --base/--head")
    if args.event != "changed" and (has_git_ref or args.changed_file):
        parser.error("--base, --head, and --changed-file require --event changed")
    return args


def _apply_existing_filters(
    decisions: list[dict],
    mode: str,
    only_set: set[str],
) -> list[dict]:
    filtered: list[dict] = []
    for decision in decisions:
        phase = decision["phase"]
        if not phase["enabled"]:
            filtered.append(decision)
        elif only_set and phase["name"] not in only_set:
            filtered.append(_decision(phase, False, "excluded by --only"))
        elif not is_selected_for_mode(phase, mode):
            filtered.append(_decision(phase, False, f"excluded by mode {mode}"))
        else:
            filtered.append(decision)
    return filtered


def repository_relative_path(path: Path, repo_root: Path) -> str | None:
    try:
        relative = path.resolve().relative_to(repo_root.resolve())
    except ValueError:
        return None
    return _normalize_changed_path(relative.as_posix())


def protect_selector_files(
    normalized_config: dict,
    config_path: Path,
    repo_root: Path,
) -> None:
    protected_paths = [
        repository_relative_path(config_path, repo_root),
        repository_relative_path(Path(__file__), repo_root),
    ]
    selector_paths = normalized_config["selection"]["selector_paths"]
    for protected_path in protected_paths:
        if protected_path is not None and protected_path not in selector_paths:
            selector_paths.append(protected_path)


def main() -> int:
    args = parse_args()
    config_path = Path(args.config)

    config = validate_config(load_config(config_path), config_path)
    protect_selector_files(config, config_path, Path.cwd())

    changed_paths: list[str] | None = None
    fallback_reason: str | None = None
    if args.event == "changed":
        if args.changed_file:
            changed_paths = sorted(set(args.changed_file))
        elif args.base is not None and args.head is not None:
            changed_paths, fallback_reason = collect_changed_files(
                Path.cwd(),
                args.base,
                args.head,
            )
        elif args.base is not None or args.head is not None:
            fallback_reason = "--base and --head must be provided together"
        else:
            fallback_reason = "no changed-file or Git base/head was provided"

    decisions = select_for_event(
        config,
        args.event,
        changed_paths,
        fallback_reason,
    )
    decisions = _apply_existing_filters(decisions, args.mode, set(args.only))
    selected_phases = [
        decision["phase"] for decision in decisions if decision["selected"]
    ]

    if args.list:
        for phase in selected_phases:
            print(phase["name"])
        return 0

    print(f"mode: {args.mode}")
    print(f"event: {args.event}")
    print(f"config: {config_path}")
    if args.event == "changed" and fallback_reason is None:
        if changed_paths:
            print(f"changed files: {len(changed_paths)}")
        else:
            print("changed files: none")
    for decision in decisions:
        outcome = "selected" if decision["selected"] else "skipped"
        print(
            f"[verify] {outcome}: {decision['name']} ({decision['reason']})"
        )

    if not selected_phases:
        print("no verification phases selected")
        return 0

    for phase in selected_phases:
        print("")
        print(f"[verify] phase: {phase['name']}")

        command = phase["command"]
        if not command:
            reason = phase["reason"]
            if reason:
                print(f"[verify] skipped: {reason}")
                continue
            print(
                f"[verify] failed: phase '{phase['name']}' has no command",
                file=sys.stderr,
            )
            return 2

        print(f"[verify] command: {command}")
        code = run_command(command)

        if code != 0:
            print(
                f"[verify] failed: {phase['name']} ( exit code {code} )",
                file=sys.stderr,
            )
            return code

        print(f"[verify] passed: {phase['name']}")

    print("")
    print("[verify] all selected phases passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
