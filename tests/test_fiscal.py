from __future__ import annotations

from gentms.fiscal import (
    actual_year_for_month,
    annual_filename,
    era_code_for_fiscal_year,
    monthly_filename,
    output_directory_name,
)


def test_actual_year_for_fiscal_month_rolls_over_after_december() -> None:
    assert actual_year_for_month(2026, 12) == 2026
    assert actual_year_for_month(2026, 1) == 2027


def test_era_code_for_fiscal_year_uses_expected_short_form() -> None:
    assert era_code_for_fiscal_year(2026) == "R8"
    assert era_code_for_fiscal_year(2019) == "H31"


def test_annual_filename_uses_fiscal_year_and_era() -> None:
    assert annual_filename(2026) == "2026年度(R8).xlsx"
    assert output_directory_name(2026) == "2026年度(R8)"


def test_monthly_filename_uses_calendar_year_for_selected_month() -> None:
    assert monthly_filename(2026, 12) == "2026-12.xlsx"
    assert monthly_filename(2026, 1) == "2027-01.xlsx"
