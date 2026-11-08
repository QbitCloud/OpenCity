import requests

API_URL = "http://127.0.0.1:8000"


# Get hospital data from the backend
def get_hospitals():
    try:
        response = requests.get(API_URL + "/hospitals", timeout=30)
        response.raise_for_status()

        hospital_data = response.json()
        return hospital_data
    except requests.RequestException:
        return None
