from fastapi import FastAPI
from SERVER.api.routes import router

app = FastAPI(
    title="OpenCity",
    version="1.0.0"
)

app.include_router(router)