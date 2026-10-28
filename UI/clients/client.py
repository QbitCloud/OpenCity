import requests

API_URL = "http://127.0.0.1:8000"


def check_backend():
    response = requests.get(
        f"{API_URL}/",
        timeout=5
    )
    response.raise_for_status()
    return response.json()
def get_waste_collection():
    response = requests.get(
        f"{API_URL}/api/waste-collection",
        timeout=10,
    )
    response.raise_for_status()
    return response.json()

