from SERVER.client.mongodb import get_database

# NJDG page for Surat district. Readings of any other district in the collection are left out.
SURAT_URL = "https://njdg.ecourts.gov.in/njdg_v3/?p=home/index&state_code=24~17&dist_code=14"


# Get Surat court data sorted by date
def get_court_data():
    database = get_database()
    collection = database["court_cases"]

    court_records = collection.find({"source_url": SURAT_URL}, {"_id": 0})
    court_records = court_records.sort("date", 1)

    return list(court_records)
