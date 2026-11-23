from SERVER.client.mongodb import get_database


# Get SMC urban health centres sorted by zone and name
def get_health_centre_data():
    database = get_database()
    collection = database["health_centres"]

    centres = collection.find({}, {"_id": 0})
    centres = centres.sort([("zone_code", 1), ("name", 1)])

    return list(centres)
