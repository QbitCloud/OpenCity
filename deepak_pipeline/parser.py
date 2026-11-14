"""Read useful Finance values from an SMC balance-sheet PDF."""
from __future__ import annotations

import re
import subprocess
import tempfile


AMOUNT_PATTERN = r"(\(?-?[\d,]+\.\d{2}\)?)"


def get_text_from_pdf(pdf_file: bytes) -> str:
    """Convert a PDF file into readable text."""
    with tempfile.NamedTemporaryFile(suffix=".pdf") as temporary_pdf:
        temporary_pdf.write(pdf_file)
        temporary_pdf.flush()

        return subprocess.check_output(
            ["pdftotext", "-layout", temporary_pdf.name, "-"],
            text=True,
        )


def convert_amount(amount: str) -> float:
    """Convert text such as '1,250.00' into 1250.0."""
    is_negative = amount.startswith("(") and amount.endswith(")")
    clean_amount = amount.strip("()").replace(",", "")
    value = float(clean_amount)

    return -value if is_negative else value


def find_value_for_label(report_text: str, label: str) -> float:
    """Find the current-year amount written beside a report label."""
    words = re.findall(r"[A-Za-z]+", label)
    flexible_label = r"[\s.,&-]*".join(re.escape(word) for word in words)

    match = re.search(
        rf"^\s*{flexible_label}\s+(?:\d+\s+)?"
        rf"{AMOUNT_PATTERN}\s+{AMOUNT_PATTERN}\s*$",
        report_text,
        re.MULTILINE | re.IGNORECASE,
    )

    if not match:
        raise ValueError(f"Could not find '{label}' in this balance sheet.")

    return convert_amount(match.group(1))


def find_total_before_section(report_text: str, section_name: str) -> float:
    """Find the total written immediately before a named report section."""
    lines = report_text.splitlines()

    for line_number, line in enumerate(lines):
        is_section_start = re.match(
            rf"^\s*{re.escape(section_name)}(?:\s|$)",
            line,
            re.IGNORECASE,
        )

        if not is_section_start:
            continue

        for previous_line in reversed(lines[:line_number]):
            match = re.match(
                rf"^\s*{AMOUNT_PATTERN}\s+{AMOUNT_PATTERN}\s*$",
                previous_line,
            )

            if match:
                return convert_amount(match.group(1))

    raise ValueError(f"Could not find the total before '{section_name}'.")


def read_balance_sheet_text(report_text: str) -> dict:
    """Read one financial year's key values from balance-sheet text."""
    year_match = re.search(
        r"(?:YEAR ENDED|AS ON)\s+31(?:ST)?\s+MARCH,?\s+(20\d{2})",
        report_text,
        re.IGNORECASE,
    )

    if not year_match:
        raise ValueError("Could not find the financial year.")

    ending_year = int(year_match.group(1))
    financial_year = f"{ending_year - 1}-{str(ending_year)[-2:]}"

    total_income = find_total_before_section(report_text, "Expenditure")
    total_expenditure = find_total_before_section(
        report_text,
        "Net Surplus for the year before taxation",
    )

    return {
        "financial_year": financial_year,
        "amount_unit": "INR",
        "finance.total_income": total_income,
        "finance.total_expenditure": total_expenditure,
        "finance.tax_revenue": find_value_for_label(
            report_text,
            "Tax Revenues",
        ),
        "finance.non_tax_revenue": find_value_for_label(
            report_text,
            "Non Tax Revenues",
        ),
        "finance.operating_balance": round(
            total_income - total_expenditure,
            2,
        ),
    }


def read_balance_sheet_pdf(pdf_file: bytes) -> dict:
    """Read Finance values directly from one PDF file."""
    report_text = get_text_from_pdf(pdf_file)
    return read_balance_sheet_text(report_text)
