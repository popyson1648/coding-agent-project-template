from __future__ import annotations

from datetime import date

from gentms.workbook import build_annual_workbook, build_monthly_workbook

EXPECTED_HEADERS = ["日付", "出勤 (時)", "出勤 (分)", "退勤 (時)", "退勤 (分)", "休暇種別"]


def test_annual_workbook_creates_fiscal_year_sheet_order() -> None:
    workbook = build_annual_workbook(2026)

    assert workbook.sheetnames == [
        "4月",
        "5月",
        "6月",
        "7月",
        "8月",
        "9月",
        "10月",
        "11月",
        "12月",
        "1月",
        "2月",
        "3月",
    ]


def test_month_sheet_uses_date_cells_and_dropdowns() -> None:
    workbook = build_monthly_workbook(2026, 4)
    worksheet = workbook["4月"]

    assert [cell.value for cell in worksheet[1]] == EXPECTED_HEADERS
    assert worksheet["A2"].value == date(2026, 4, 1)
    assert worksheet["A2"].number_format == "d"
    assert worksheet.max_row == 31
    assert len(worksheet.data_validations.dataValidation) == 5
    assert (
        worksheet.data_validations.dataValidation[0].formula1
        == '"6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22"'
    )
    assert worksheet.data_validations.dataValidation[4].formula1 == '"年休,忌引"'
