from SERVER.client.mongodb import get_database


# Get Surat hospital data sorted by name
def get_hospital_data():
    database = get_database()
    collection = database["hospitals"]

    hospital_records = collection.find({}, {"_id": 0})
    hospital_records = hospital_records.sort("name", 1)

    return list(hospital_records)
