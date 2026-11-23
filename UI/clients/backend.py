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


# Get SMC urban health centres from the backend
def get_health_centres():
    try:
        response = requests.get(API_URL + "/health-centres", timeout=30)
        response.raise_for_status()
        return response.json()
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


# Get SMC officials from the backend.
def get_officials():
    try:
        response = requests.get(API_URL + "/officials", timeout=30)
        response.raise_for_status()
        return response.json()
    except requests.RequestException:
        return None


# Get the posts responsible for the court figures from the backend.
def get_court_officials():
    try:
        response = requests.get(API_URL + "/court-officials", timeout=30)
        response.raise_for_status()
        return response.json()
    except requests.RequestException:
        return None


# Generate an RTI from the selected issue.
def generate_rti(context):
    try:
        response = requests.post(API_URL + "/rti/generate", json={"context": context}, timeout=240)
        response.raise_for_status()
        return response.json()["text"]
    except (requests.RequestException, ValueError, KeyError):
        return None
