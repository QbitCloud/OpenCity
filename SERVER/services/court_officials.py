from SERVER.client.mongodb import get_database


# Posts responsible for the court figures, sorted by designation
def get_court_officials_data():
    database = get_database()
    collection = database["court_officials"]
    officials = collection.find({}, {"_id": 0}).sort("designation", 1)
    return list(officials)
