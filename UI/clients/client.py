import requests

API_URL = "http://127.0.0.1:8000"


def check_backend():
    response = requests.get(
        f"{API_URL}/",
        timeout=5
    )
    response.raise_for_status()
    return response.json()
def get_finance_summary():
    response = requests.get(
        f"{API_URL}/api/finance-summary",
        timeout=10,
    )
    response.raise_for_status()
    return response.json()


def get_deepak_finance_analysis():
    response = requests.get(
        f"{API_URL}/api/deepak-finance",
        timeout=10,
    )
    response.raise_for_status()
    return response.json()


def get_deepak_water_analysis():
    response = requests.get(
        f"{API_URL}/api/deepak-water",
        timeout=10,
    )
    response.raise_for_status()
    return response.json()

