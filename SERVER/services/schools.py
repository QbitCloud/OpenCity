from SERVER.client.mongodb import get_database


# Get Surat school data sorted by year
def get_school_data():
    database = get_database()
    collection = database["school_overview"]

    school_records = collection.find({"regionCode": "2422"}, {"_id": 0})
    school_records = school_records.sort("yearId", 1)

    return list(school_records)
