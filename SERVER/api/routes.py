from fastapi import HTTPException
from SERVER.services.finance import load_finance_summary
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


@router.get("/api/finance-summary")
def finance_summary():
    try:
        data = load_finance_summary()
    except FileNotFoundError:
        raise HTTPException(
            status_code=503,
            detail="Finance data is unavailable. Run the finance pipeline first.",
        )

    if not data["metrics"]:
        raise HTTPException(
            status_code=503,
            detail="No reported finance observations are available.",
        )
    return data
