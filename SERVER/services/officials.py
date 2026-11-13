from SERVER.client.mongodb import get_database


# SMC officials sorted by category and name
def get_officials_data():
    database = get_database()
    collection = database["smc_officials"]
    officials = collection.find({}, {"_id": 0}).sort([("category", 1), ("name", 1)])
    return list(officials)
