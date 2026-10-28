from fastapi import HTTPException
from SERVER.services.waste_collection import load_waste_collection
from fastapi import APIRouter

router = APIRouter()


@router.get("/")
async def root():
    return {"message": "Hello World"}


@router.get("/hello/{name}")
async def say_hello(name: str):
    return {"message": f"Hello {name}"}

@router.get("/api/waste-collection")
def waste_collection():
    try:
        data = load_waste_collection()
    except FileNotFoundError:
        raise HTTPException(
            status_code=503,
            detail="Waste-collection data is unavailable. Run the pipeline first.",
        )

    if not data["observations"]:
        raise HTTPException(
            status_code=503,
            detail="No door-to-door waste-collection observations are available.",
        )

    return data
