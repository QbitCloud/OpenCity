import requests

API_URL = "http://127.0.0.1:8000"


# Get school data from the backend
def get_schools():
    try:
        response = requests.get(API_URL + "/schools", timeout=30)
        response.raise_for_status()

        school_data = response.json()
        return school_data
    except requests.RequestException:
        return None
