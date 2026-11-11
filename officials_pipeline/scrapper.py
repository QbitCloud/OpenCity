import requests
from bs4 import BeautifulSoup

from officials_pipeline.categories import get_category

URL = "https://www.suratmunicipal.gov.in/Home/SMCOfficials"


# Fetch the officials page.
def fetch_page():
    page = requests.get(URL, headers={"User-Agent": "Mozilla/5.0"}, timeout=30)
    page.raise_for_status()
    return page.content


# Get text from the matching fields.
def get_text(officer, selector):
    values = []
    for field in officer.select(selector):
        values.append(field.get_text(" ", strip=True))

    return ", ".join(values)


# Read the officials and their contact details.
def scrape_officials(html):
    soup = BeautifulSoup(html, "html.parser")
    sections = {
        "Municipal Commissioner": ".contact-block-custom",
        "Administrative": "ul.administrative > li.contact-block",
        "Engineering": "ul.Engineering > li.contact-block",
        "Health": "ul.health > li.contact-block",
    }
    officials = []

    for section_name, selector in sections.items():
        officers = soup.select(selector)
        if not officers:
            raise ValueError(f"SMC officials section not found: {section_name}")

        for officer in officers:
            name = get_text(officer, ".name")
            designation = get_text(officer, ".designation")
            if not name or not designation:
                raise ValueError("An SMC official has no name or designation.")

            category = get_category(designation, section_name)

            emails = []
            for field in officer.select(".contact-email"):
                email = field.get_text(strip=True)
                if "govdotin" in field.get("class", []):
                    email += "[at]suratmunicipal[dot]gov[dot]in"

                email = email.replace("[at]", "@").replace("[dot]", ".")
                emails.append(email)

            mobile_numbers = []
            office_numbers = []
            for field in officer.select(".contact-mobile, .officeTelephone"):
                phone = field.get_text(" ", strip=True)
                if phone.startswith("(O)"):
                    office_numbers.append(phone.removeprefix("(O)").strip())
                else:
                    mobile_numbers.append(phone.removeprefix("(M)").strip())

            officials.append({
                "name": name,
                "designation": designation,
                "category": category,
                "zone": get_text(officer, ".text-bold"),
                "mobile": ", ".join(mobile_numbers),
                "office_phone": ", ".join(office_numbers),
                "emails": emails,
            })

    return officials
