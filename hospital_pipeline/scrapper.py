import time
import requests
from bs4 import BeautifulSoup

URL = "https://surat.nic.in/public-utility-category/hospitals/"


def fetch_page(page_no):
    # Download one page of the hospital list.
    page = requests.get(f"{URL}page/{page_no}/", headers={"User-Agent": "Mozilla/5.0"}, timeout=30)
    # The website returns 404 after the last page.
    if page.status_code == 404:
        return None
    page.raise_for_status()
    return page.content


def scrape_page(html):
    soup = BeautifulSoup(html, "html.parser")

    hospitals = []
    for box in soup.find_all("li", class_="public-utlty-catg"):
        hospital = {
            "name": box.find("h2").get_text(strip=True),
            "address": None,
            "phone": None,
            "category": None,
            "pincode": None,
        }

        listing = box.find("ul", class_="pubutility-list")
        for row in listing.find_all("li"):
            # Join the text into one line.
            text = " ".join(row.get_text(" ", strip=True).split())

            # Every detail has a label except the address.
            if text.startswith("Phone :"):
                hospital["phone"] = text.replace("Phone :", "").strip()
            elif text.startswith("Category/Type :"):
                hospital["category"] = text.replace("Category/Type :", "").strip()
            elif text.startswith("Pincode :"):
                hospital["pincode"] = text.replace("Pincode :", "").strip()
            else:
                hospital["address"] = text

        hospitals.append(hospital)
    return hospitals


def scrape_hospitals():
    hospitals = []
    page_no = 1
    while True:
        html = fetch_page(page_no)
        if html is None:
            break

        rows = scrape_page(html)
        if not rows:
            break

        hospitals.extend(rows)
        page_no += 1
        time.sleep(2)  # Wait before requesting the next page.

    if not hospitals:
        raise ValueError("No hospitals found")
    return hospitals
