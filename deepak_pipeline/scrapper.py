"""Find official Surat Municipal Corporation Finance and Water reports."""
from __future__ import annotations

import re
from html.parser import HTMLParser
import time
from urllib.parse import urljoin

import requests

BALANCE_SHEET_INDEX = "https://www.suratmunicipal.gov.in/Departments/Accounts/BalanceSheet"
WATER_QUALITY_INDEX = "https://www.suratmunicipal.gov.in/Departments/HydraulicWaterQuality"
HEADERS = {"User-Agent": "OpenCity student project"}


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
    response = requests.get(BALANCE_SHEET_INDEX, headers=HEADERS, timeout=30)
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


def fetch_document(url: str) -> bytes:
    """Download one official balance-sheet PDF."""
    response = requests.get(url, headers=HEADERS, timeout=60)
    response.raise_for_status()
    return response.content


def discover_water_quality_reports() -> dict[tuple[int, int], str]:
    """Return official monthly Water Quality PDFs keyed by year and month."""
    response = requests.get(WATER_QUALITY_INDEX, headers=HEADERS, timeout=30)
    response.raise_for_status()

    parser = Links()
    parser.feed(response.text)

    reports: dict[tuple[int, int], str] = {}
    for href in parser.links:
        url = urljoin(WATER_QUALITY_INDEX, href)
        match = re.search(r"/WaterQuality/(20\d{2})/(\d{2})\.pdf", url, re.IGNORECASE)
        if match:
            reports[(int(match.group(1)), int(match.group(2)))] = url

    return dict(sorted(reports.items()))


def polite_pause() -> None:
    """Keep repeated requests to the public SMC site modest."""
    time.sleep(1)
