from fastapi import FastAPI

from SERVER.api.routes import router
from SERVER.client.mongodb import connect_mongodb

# Intial Function call for running the Database.
connect_mongodb()

app = FastAPI(title="OpenCity",version="1.0.0")

app.include_router(router)
