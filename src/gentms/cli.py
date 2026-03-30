from __future__ import annotations

import argparse
import sys
from pathlib import Path

from gentms.fiscal import annual_filename, monthly_filename, output_directory_name
from gentms.workbook import (
    build_annual_workbook,
    build_monthly_workbook,
    ensure_output_paths_do_not_exist,
    save_workbook,
)


class CliError(Exception):
    pass


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(preprocess_args(argv or sys.argv[1:]))

    try:
        if args.command == "annual":
            run_annual(args.year, args.create_dir)
        elif args.command == "monthly":
            run_monthly(args.year, args.months, args.create_dir)
        else:
            raise CliError(f"unsupported command: {args.command}")
    except (CliError, FileExistsError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="gentms")
    subparsers = parser.add_subparsers(dest="command", required=True)

    annual = subparsers.add_parser("annual", help="Generate one workbook for a fiscal year.")
    annual.add_argument("year", type=parse_year)
    annual.add_argument("--create-dir", action="store_true", help="Create an output directory.")

    monthly = subparsers.add_parser("monthly", help="Generate workbooks for selected months.")
    monthly.add_argument("year", type=parse_year)
    monthly.add_argument("months", nargs="+", type=parse_month)
    monthly.add_argument("--create-dir", action="store_true", help="Create an output directory.")

    return parser


def preprocess_args(argv: list[str]) -> list[str]:
    if argv and argv[0].isdigit():
        return ["annual", *argv]
    return argv


def parse_year(value: str) -> int:
    try:
        year = int(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError("year must be an integer") from exc
    if year < 1868:
        raise argparse.ArgumentTypeError("year must be 1868 or later")
    return year


def parse_month(value: str) -> int:
    try:
        month = int(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError("month must be an integer") from exc
    if month < 1 or month > 12:
        raise argparse.ArgumentTypeError("month must be between 1 and 12")
    return month


def run_annual(year: int, create_dir: bool) -> None:
    output_directory = prepare_output_directory(Path.cwd(), year, create_dir)
    output_path = output_directory / annual_filename(year)
    ensure_output_paths_do_not_exist([output_path])

    workbook = build_annual_workbook(year)
    save_workbook(workbook, output_path)


def run_monthly(year: int, months: list[int], create_dir: bool) -> None:
    duplicates = _find_duplicate_months(months)
    if duplicates:
        labels = ", ".join(str(month) for month in duplicates)
        raise CliError(f"duplicate months are not allowed: {labels}")

    output_directory = prepare_output_directory(Path.cwd(), year, create_dir)
    ordered_paths = [output_directory / monthly_filename(year, month) for month in months]
    ensure_output_paths_do_not_exist(ordered_paths)

    for month, output_path in zip(months, ordered_paths, strict=True):
        workbook = build_monthly_workbook(year, month)
        save_workbook(workbook, output_path)


def prepare_output_directory(base_directory: Path, year: int, create_dir: bool) -> Path:
    if not create_dir:
        return base_directory

    target_directory = base_directory / output_directory_name(year)
    ensure_output_paths_do_not_exist([target_directory])
    target_directory.mkdir()
    return target_directory


def _find_duplicate_months(months: list[int]) -> list[int]:
    seen: set[int] = set()
    duplicates: list[int] = []
    for month in months:
        if month in seen and month not in duplicates:
            duplicates.append(month)
        seen.add(month)
    return duplicates
