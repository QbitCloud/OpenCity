from SERVER.client.mongodb import get_database


# Get Surat court data sorted by date
def get_court_data():
    database = get_database()
    collection = database["court_cases"]

    court_records = collection.find({}, {"_id": 0})
    court_records = court_records.sort("date", 1)

    return list(court_records)
