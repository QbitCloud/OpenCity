import requests

API_URL = "http://127.0.0.1:8000"


# Get court data from the backend
def get_courts():
    try:
        response = requests.get(API_URL + "/courts", timeout=30)
        response.raise_for_status()

        court_data = response.json()
        return court_data
    except requests.RequestException:
        return None
