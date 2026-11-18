from pymongo import MongoClient
from pymongo.errors import PyMongoError

from court_pipeline.responsible import RESPONSIBLE
from court_pipeline.scrapper import URL

is_connected = False

try:
    client = MongoClient(
        "mongodb+srv://meparaglide_db_user:EJQRL7po8sIkrXZx@opencity.gtsikl8.mongodb.net/",
        serverSelectionTimeoutMS=10000,
    )
    client.admin.command("ping")
    collection = client["opencity"]["court_cases"]
    is_connected = True
except PyMongoError:
    print("MongoDB connection failed")


def save_courts(courts, scraped_at):
    if not courts:
        raise ValueError("No new data, Existing records were kept.")

    # Add the source, fetch time and the day of this reading.
    courts["source_url"] = URL
    courts["scraped_at"] = scraped_at
    courts["date"] = scraped_at[:10]

    # Add the post responsible for each figure, and the judge holding it. The sources are in responsible.py.
    courts["responsible"] = RESPONSIBLE

    # Keep one reading per day. Replace today's reading if it was already saved.
    collection.delete_many({"source_url": URL, "date": courts["date"]})
    collection.insert_one(courts)
