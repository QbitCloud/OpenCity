import time
import requests

URL = "https://api.udiseplus.gov.in/open-services/v1.1/kpi/edu-highlights"


def fetch_year(year_id):
    # Request one year's data.
    body = {
        "yearId": year_id, 
        "regionCode": "2422", 
        "regionType": 12, 
        "valueType": 1
    }
    response = requests.post(URL, json=body, timeout=30)
    response.raise_for_status()
    result = response.json()
    if result["status"] is not True:
        raise ValueError(f"API request failed for yearId {year_id}")
    return result["data"]


def scrape_schools(year_id):
    schools = []
    while True:
        data = fetch_year(year_id)
        if not data:
            print(f"No data for yearId {year_id} Stopped.")
            break

        schools.append(data[0])
        year_id += 1
        time.sleep(2)  # Wait before requesting the next year.
    return schools
