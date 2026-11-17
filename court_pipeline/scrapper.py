import requests
from bs4 import BeautifulSoup

# National Judicial Data Grid page for Gujarat (24~17) and Surat district (14).
URL = "https://njdg.ecourts.gov.in/njdg_v3/?p=home/index&state_code=24~17&dist_code=14"


def fetch_page():
    # Download the webpage.
    page = requests.get(URL, headers={"User-Agent": "Mozilla/5.0"}, timeout=60)
    page.raise_for_status()
    return page.content


def to_number(text):
    # Turn "73,554 (51%)" into 73554.
    return int(text.split()[0].replace(",", ""))


def scrape_courts(html):
    soup = BeautifulSoup(html, "html.parser")

    # Make sure the page is showing Surat district.
    selected = [option.get_text(strip=True) for option in soup.find_all("option", selected=True)]
    if "SURAT" not in selected:
        raise ValueError("Surat district page not found")

    # Read the cards at the top of the page.
    cards = {}
    for heading in soup.find_all("h4", class_="card-title"):
        value = heading.find_next_sibling("span")
        if value is not None:
            title = " ".join(heading.get_text().split())
            cards[title] = value.get_text(strip=True)

    courts = {
        "civil_pending": to_number(cards["Civil Cases"]),
        "criminal_pending": to_number(cards["Criminal Cases"]),
        "total_pending": to_number(cards["Total Cases"]),
        "pre_litigation": to_number(cards["Pre-Litigation / Pre-Trial"]),
        "particulars": [],
        "pending_by_age": [],
    }

    # Read the "Particulars" table: cases filed and disposed last month, and cases filed by women and senior citizens.
    table = None
    for heading in soup.find_all("th"):
        if heading.get_text(strip=True) == "Particulars":
            table = heading.find_parent("table")
            break
    if table is None:
        raise ValueError("Particulars table not found")

    for row in table.find("tbody").find_all("tr"):
        columns = [column.get_text(strip=True) for column in row.find_all("td")]
        # Skip rows that have no numbers.
        if len(columns) != 4 or not columns[1]:
            continue

        courts["particulars"].append({
            # Read the name exactly as shown on the website.
            "name": columns[0],
            "civil": to_number(columns[1]),
            "criminal": to_number(columns[2]),
            "total": to_number(columns[3]),
        })

    # Read the pending cases by age. Every age has a heading row and a numbers row.
    table = None
    for heading in soup.find_all("h6"):
        if heading.get_text(strip=True) == "Less than one year":
            table = heading.find_parent("table")
            break
    if table is None:
        raise ValueError("Age wise table not found")

    for heading in table.find_all("h6"):
        numbers = heading.find_parent("tr").find_next_sibling("tr").find_all("a")
        courts["pending_by_age"].append({
            "age": heading.get_text(strip=True),
            "civil": to_number(numbers[0].get_text(strip=True)),
            "criminal": to_number(numbers[1].get_text(strip=True)),
            "total": to_number(numbers[2].get_text(strip=True)),
        })

    if not courts["particulars"] or not courts["pending_by_age"]:
        raise ValueError("No court data found")
    return courts
