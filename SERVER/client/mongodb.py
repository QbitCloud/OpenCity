from pymongo import MongoClient
from pymongo.errors import PyMongoError


client = None


# Connect to Database
def connect_mongodb():
    global client

    client = MongoClient(
        "mongodb+srv://meparaglide_db_user:EJQRL7po8sIkrXZx@opencity.gtsikl8.mongodb.net/",
        serverSelectionTimeoutMS=10000,
    )
    try:
        client.admin.command("ping")
    except PyMongoError:
        client.close()
        raise


# Return the database
def get_database():
    return client["opencity"]
