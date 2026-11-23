import requests
from bs4 import BeautifulSoup

URL = "https://www.suratmunicipal.gov.in/Departments/PMJAYUHC"


def fetch_page():
    # Download the webpage.
    page = requests.get(URL, headers={"User-Agent": "Mozilla/5.0"}, timeout=30)
    page.raise_for_status()
    return page.content


def scrape_centres(html):
    soup = BeautifulSoup(html, "html.parser")
    content = soup.find("div", class_="contentblock")
    if content is None:
        raise ValueError("Health centres section not found")

    centres = []
    for heading in content.find_all("h2"):
        # Read the zone exactly as shown on the website.
        zone = heading.get_text(strip=True)
        listing = heading.find_next_sibling("ul")
        for row in listing.find_all("li"):
            # Skip the column headings.
            if "hidden-xs" in row.get("class", []):
                continue

            # Read the first column and remove its "Name" label.
            details = row.find("div", class_="row")
            column = details.find("div")
            label = column.find("div")
            label.decompose()
            name = column.get_text(strip=True)

            # Find the facility type from its name.
            if "UCHC" in name:
                facility_type = "uchc"
            elif "UHC" in name or "URBAN HEALTH" in name:
                facility_type = "uhc"
            else:
                raise ValueError(f"Unknown centre type: {name}")

            centres.append({
                "name": name,
                "facility_type": facility_type,
                # MH means an attached maternity home.
                "maternity_home": name.endswith(" MH"),
                "zone_code": zone,
            })

    if not centres:
        raise ValueError("No health centres found")
    return centres
