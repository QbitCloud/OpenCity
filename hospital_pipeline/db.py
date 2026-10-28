from pymongo import MongoClient
from pymongo.errors import PyMongoError

from hospital_pipeline.scrapper import URL

is_connected = False

try:
    client = MongoClient(
        "mongodb+srv://meparaglide_db_user:EJQRL7po8sIkrXZx@opencity.gtsikl8.mongodb.net/",
        serverSelectionTimeoutMS=10000,
    )
    client.admin.command("ping")
    collection = client["opencity"]["hospitals"]
    is_connected = True
except PyMongoError:
    print("MongoDB connection failed")


def save_hospitals(hospitals, scraped_at):
    if not hospitals:
        raise ValueError("No new data, Existing records were kept.")

    # Add the source and fetch time.
    for hospital in hospitals:
        hospital["source_url"] = URL
        hospital["scraped_at"] = scraped_at

    # Replace this source's records with the new list.
    collection.delete_many({"source_url": URL})
    collection.insert_many(hospitals)
