"""SMC annual finance data from the published balance sheet PDF."""
from __future__ import annotations

import re

from ..model import Metric, Obs, Raw, Result, Source, ValidationError
from ..parse import fy_period, num, pdf_text
from ..surat import SMC

URL = 'https://www.suratmunicipal.gov.in/Content/Documents/Departments/Accounts/BalanceSheet_25_26.pdf'

SOURCE = Source(
    id='smc_balance_sheet',
    name='SMC balance sheet and income statement',
    publisher='Surat Municipal Corporation, Accounts Department',
    url=URL,
    module='finance',
    cadence='annual',
    interval_hours=24 * 365,
    geo_note='SMC city (whole corporation area)',
    licence_note='Surat Municipal Corporation published financial statement',
    metrics=(
        Metric('finance.tax_revenue', 'Tax revenue', 'rupees'),
        Metric('finance.non_tax_revenue', 'Non-tax revenue', 'rupees'),
        Metric('finance.government_grants_subsidies', 'Government grants and subsidies', 'rupees'),
        Metric('finance.octroi_compensation', 'Compensation in lieu of octroi', 'rupees'),
        Metric('finance.other_income', 'Other income', 'rupees'),
        Metric('finance.total_income', 'Total income', 'rupees'),
        Metric('finance.employee_payments_benefits', 'Employee payments and benefits', 'rupees'),
        Metric('finance.total_expenditure', 'Total expenditure', 'rupees'),
        Metric('finance.net_surplus_before_tax', 'Net surplus before taxation', 'rupees'),
        Metric('finance.excess_income_over_expenditure', 'Excess of income over expenditure', 'rupees'),
    ),
)

ITEMS = {
    'Tax Revenues': 'finance.tax_revenue',
    'Non Tax Revenues': 'finance.non_tax_revenue',
    'Govt. Grants, Contri. & Subsidies': 'finance.government_grants_subsidies',
    'Compensation in lieu of Octroi': 'finance.octroi_compensation',
    'Other Income': 'finance.other_income',
    'Payments & Benefits to Employees': 'finance.employee_payments_benefits',
    'Net Surplus for the year before taxation': 'finance.net_surplus_before_tax',
    'Excess of Income Over Expenditure': 'finance.excess_income_over_expenditure',
}

NUMBER = r'(-?[\d,]+\.\d{2}|-)'


def fetch(ctx):
    yield ctx.get(URL, skip_if_seen=True)


def _pair(text: str, label: str) -> tuple[float | None, float | None]:
    """Return the current and comparative values printed after a statement label."""
    pattern = rf'^\s*{re.escape(label)}\s+(?:\d+\s+)?{NUMBER}\s+{NUMBER}\s*$'
    match = re.search(pattern, text, flags=re.MULTILINE)
    if not match:
        raise ValidationError(f'could not find {label!r} in the income statement')
    return num(match.group(1)), num(match.group(2))


def _statement(text: str) -> str:
    match = re.search(
        r'INCOME AND EXPENDITURE ACCOUNT FOR THE YEAR ENDED 31 MARCH,?\s+(20\d{2})(.*?)(?:Notes forming part of Accounts|$)',
        text,
        flags=re.DOTALL | re.IGNORECASE,
    )
    if not match:
        raise ValidationError('income and expenditure statement was not found in the PDF')
    return match.group(0)


def _total_before(statement: str, heading: str, metric_name: str) -> tuple[float | None, float | None]:
    """Read the unlabelled total line immediately before a statement heading."""
    lines = statement.splitlines()
    heading_index = next(
        (i for i in range(len(lines) - 1, -1, -1) if re.match(rf'^\s*{re.escape(heading)}(?:\s|$)', lines[i], re.IGNORECASE)),
        None,
    )
    if heading_index is None:
        raise ValidationError(f'could not find heading for total {metric_name}')
    for line in reversed(lines[:heading_index]):
        match = re.match(rf'^\s*{NUMBER}\s+{NUMBER}\s*$', line)
        if match:
            return num(match.group(1)), num(match.group(2))
    raise ValidationError(f'could not find total {metric_name}')


def parse(raw: Raw) -> Result:
    statement = _statement(pdf_text(raw.body))
    year_match = re.search(r'YEAR ENDED 31 MARCH,?\s+(20\d{2})', statement, flags=re.IGNORECASE)
    assert year_match is not None
    current_year = int(year_match.group(1)) - 1
    years = (current_year, current_year - 1)
    values = {metric: _pair(statement, label) for label, metric in ITEMS.items()}
    values['finance.total_income'] = _total_before(statement, 'Expenditure', 'income')
    values['finance.total_expenditure'] = _total_before(statement, 'Net Surplus for the year before taxation', 'expenditure')

    result = Result(geos=[SMC])
    for metric_id, pair in values.items():
        for year, value in zip(years, pair):
            start, end = fy_period(year)
            result.observations.append(Obs(
                metric_id, 'smc_city', 'smc', start, end, value=value,
                status='reported' if value is not None else 'not_reported',
            ))
    return result


def validate(result: Result, raw: Raw) -> None:
    expected = len(SOURCE.metrics) * 2
    if len(result.observations) != expected:
        raise ValidationError(f'expected {expected} finance observations, got {len(result.observations)}')
    for observation in result.observations:
        if observation.value is not None and observation.metric_id != 'finance.net_surplus_before_tax' and observation.value < 0:
            raise ValidationError(f'unexpected negative value for {observation.metric_id}')
