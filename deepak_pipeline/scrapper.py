"""Find official Surat Municipal Corporation balance sheets."""
from __future__ import annotations

import re
from html.parser import HTMLParser
from urllib.parse import urljoin

import requests

BALANCE_SHEET_INDEX = "https://www.suratmunicipal.gov.in/Departments/Accounts/BalanceSheet"


class Links(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links: list[str] = []

    def handle_starttag(self, tag, attrs):
        if tag == "a":
            href = dict(attrs).get("href")
            if href:
                self.links.append(href)


def discover_balance_sheets() -> dict[int, str]:
    response = requests.get(BALANCE_SHEET_INDEX, timeout=30)
    response.raise_for_status()

    parser = Links()
    parser.feed(response.text)

    reports: dict[int, str] = {}
    for href in parser.links:
        url = urljoin(BALANCE_SHEET_INDEX, href)
        match = re.search(r"BalanceSheet_(\d{2})_(\d{2})\.pdf", url, re.IGNORECASE)
        if match:
            reports[2000 + int(match.group(1))] = url

    return dict(sorted(reports.items()))
