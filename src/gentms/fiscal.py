from __future__ import annotations

import calendar
from dataclasses import dataclass
from datetime import date

FISCAL_MONTHS = (4, 5, 6, 7, 8, 9, 10, 11, 12, 1, 2, 3)


@dataclass(frozen=True)
class Era:
    english_code: str
    japanese_name: str
    start_date: date


ERAS = (
    Era(english_code="R", japanese_name="令和", start_date=date(2019, 5, 1)),
    Era(english_code="H", japanese_name="平成", start_date=date(1989, 1, 8)),
    Era(english_code="S", japanese_name="昭和", start_date=date(1926, 12, 25)),
    Era(english_code="T", japanese_name="大正", start_date=date(1912, 7, 30)),
    Era(english_code="M", japanese_name="明治", start_date=date(1868, 10, 23)),
)


@dataclass(frozen=True)
class YearMonth:
    year: int
    month: int


class FiscalYearError(ValueError):
    pass


def actual_year_for_month(fiscal_year: int, month: int) -> int:
    validate_year(fiscal_year)
    validate_month(month)
    return fiscal_year if month >= 4 else fiscal_year + 1


def resolve_year_month(fiscal_year: int, month: int) -> YearMonth:
    return YearMonth(year=actual_year_for_month(fiscal_year, month), month=month)


def iter_month_dates(fiscal_year: int, month: int) -> list[date]:
    resolved = resolve_year_month(fiscal_year, month)
    _, last_day = calendar.monthrange(resolved.year, resolved.month)
    return [date(resolved.year, resolved.month, day) for day in range(1, last_day + 1)]


def era_for_fiscal_year(fiscal_year: int) -> Era:
    validate_year(fiscal_year)
    fiscal_year_start = date(fiscal_year, 4, 1)
    for era in ERAS:
        if fiscal_year_start >= era.start_date:
            return era
    raise FiscalYearError("supported fiscal years must be 1868 or later")


def era_year_for_fiscal_year(fiscal_year: int) -> int:
    era = era_for_fiscal_year(fiscal_year)
    return fiscal_year - era.start_date.year + 1


def era_code_for_fiscal_year(fiscal_year: int) -> str:
    era = era_for_fiscal_year(fiscal_year)
    return f"{era.english_code}{era_year_for_fiscal_year(fiscal_year)}"


def era_display_for_fiscal_year(fiscal_year: int) -> str:
    era = era_for_fiscal_year(fiscal_year)
    return f"{era.japanese_name}{era_year_for_fiscal_year(fiscal_year)}年"


def annual_filename(fiscal_year: int) -> str:
    return f"{fiscal_year}年度({era_code_for_fiscal_year(fiscal_year)}).xlsx"


def output_directory_name(fiscal_year: int) -> str:
    return f"{fiscal_year}年度({era_code_for_fiscal_year(fiscal_year)})"


def monthly_filename(fiscal_year: int, month: int) -> str:
    resolved = resolve_year_month(fiscal_year, month)
    return f"{resolved.year}-{resolved.month:02d}.xlsx"


def sheet_name(month: int) -> str:
    validate_month(month)
    return f"{month}月"


def validate_year(value: int) -> int:
    if value < 1868:
        raise FiscalYearError("year must be 1868 or later")
    return value


def validate_month(value: int) -> int:
    if value < 1 or value > 12:
        raise FiscalYearError("month must be between 1 and 12")
    return value
