import requests

from opencity_settings import API_URL


# Get hospital data from the backend
def get_hospitals():
    try:
        response = requests.get(API_URL + "/hospitals", timeout=30)
        response.raise_for_status()

        hospital_data = response.json()
        return hospital_data
    except requests.RequestException:
        return None

# Get court data from the backend
def get_courts():
    try:
        response = requests.get(API_URL + "/courts", timeout=30)
        response.raise_for_status()

        court_data = response.json()
        return court_data
    except requests.RequestException:
        return None

# Get school data from the backend
def get_schools():
    try:
        response = requests.get(API_URL + "/schools", timeout=30)
        response.raise_for_status()

        school_data = response.json()
        return school_data
    except requests.RequestException:
        return None
