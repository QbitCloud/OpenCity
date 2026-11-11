from pymongo import MongoClient
from pymongo.errors import PyMongoError

from officials_pipeline.scrapper import URL

is_connected = False

try:
    client = MongoClient(
        "mongodb+srv://meparaglide_db_user:EJQRL7po8sIkrXZx@opencity.gtsikl8.mongodb.net/",
        serverSelectionTimeoutMS=10000,
    )
    client.admin.command("ping")
    collection = client["opencity"]["smc_officials"]
    is_connected = True
except PyMongoError:
    print("MongoDB connection failed")


# Save the latest officials in place of the old records.
def save_officials(officials, scraped_at):
    if not officials:
        raise ValueError("No new officials. Existing records were kept.")

    for official in officials:
        official["source_url"] = URL
        official["scraped_at"] = scraped_at

    collection.delete_many({"source_url": URL})
    collection.insert_many(officials)
