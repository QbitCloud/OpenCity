from pymongo import MongoClient
from pymongo.errors import PyMongoError

from PIPELINE.court_pipeline.scrapper import URL
from opencity_settings import MONGODB_DB, MONGODB_URI

is_connected = False
SOURCE_URL = "https://surat.dcourts.gov.in/list-of-judges/"
CHECKED_ON = "2026-11-18"

DISTRICT_JUDGE = {
    "post": "Principal District and Sessions Judge, Surat",
    "name": "Mr. R. A. Trivedi",
}
CHIEF_JUDICIAL_MAGISTRATE = {
    "post": "Chief Judicial Magistrate, Surat",
    "name": "Mr. Y. I. Shaikh",
}
RESPONSIBLE = {
    "total_pending": DISTRICT_JUDGE,
    "civil_pending": DISTRICT_JUDGE,
    "criminal_pending": CHIEF_JUDICIAL_MAGISTRATE,
    "pre_litigation": CHIEF_JUDICIAL_MAGISTRATE,
    "Cases Instituted in Last Month": DISTRICT_JUDGE,
    "Cases Disposed in Last Month": DISTRICT_JUDGE,
    "Filed Cases By Woman": DISTRICT_JUDGE,
    "Filed Cases By Senior Citizen": DISTRICT_JUDGE,
    "pending_by_age": DISTRICT_JUDGE,
}

try:
    client = MongoClient(MONGODB_URI, serverSelectionTimeoutMS=10000)
    client.admin.command("ping")
    collection = client[MONGODB_DB]["court_cases"]
    officials_collection = client[MONGODB_DB]["court_officials"]
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


# Save the posts responsible for the court figures, one record per post, shaped like the SMC officials.
def save_court_officials():
    officials = {}
    for figure, person in RESPONSIBLE.items():
        if person["post"] not in officials:
            officials[person["post"]] = {
                "name": person["name"] or "",
                "designation": person["post"],
                "mobile": "",
                "office_phone": "",
                "emails": [],
                # The court figures this post answers for: the keys of RESPONSIBLE
                "figures": [],
                "source_url": SOURCE_URL,
                "checked_on": CHECKED_ON,
            }
        officials[person["post"]]["figures"].append(figure)

    officials_collection.delete_many({"source_url": SOURCE_URL})
    officials_collection.insert_many(list(officials.values()))
