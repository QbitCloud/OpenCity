from pymongo import MongoClient
from school_pipeline.scrapper import URL

# Create a separate client for this pipeline.
client = MongoClient(
    "mongodb+srv://meparaglide_db_user:EJQRL7po8sIkrXZx@opencity.gtsikl8.mongodb.net/",
    serverSelectionTimeoutMS=10000,
)
collection = client["opencity"]["school_overview"]


def next_year():
    school = collection.find_one({"regionCode": "2422", "source_url": URL}, sort=[("yearId", -1)])
    if school:
        return school["yearId"] + 1
    return 11


def save_schools(schools, scraped_at):
    # Insert only if this year is not already saved.
    for school in schools:
        year = school["yearId"] + 2013
        school["academic_year"] = f"{year}-{str(year + 1)[-2:]}"
        school["source_url"] = URL
        school["scraped_at"] = scraped_at
        filters = {"regionCode": "2422", "yearId": school["yearId"], "source_url": URL}
        if not collection.find_one(filters):
            collection.insert_one(school)
