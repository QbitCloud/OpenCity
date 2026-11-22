from pymongo import MongoClient
from pymongo.errors import PyMongoError

from opencity_settings import MONGODB_DB, MONGODB_URI


client = None


# Connect to Database
def connect_mongodb():
    global client

    client = MongoClient(MONGODB_URI, serverSelectionTimeoutMS=10000)
    try:
        client.admin.command("ping")
    except PyMongoError:
        client.close()
        raise


# Return the database
def get_database():
    return client[MONGODB_DB]
