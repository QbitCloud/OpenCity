from fastapi import HTTPException
from SERVER.services.deepak_finance import load_deepak_finance_analysis
from SERVER.services.deepak_water import load_deepak_water_analysis
from SERVER.services.finance import load_finance_summary
from fastapi import APIRouter

router = APIRouter()


@router.get("/")
async def root():
    return {"message": "Hello World"}


@router.get("/hello/{name}")
async def say_hello(name: str):
    return {"message": f"Hello {name}"}

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


@router.get("/api/deepak-finance")
def deepak_finance_analysis():
    data = load_deepak_finance_analysis()

    if not data["history"]:
        raise HTTPException(
            status_code=503,
            detail="Historic Finance data is unavailable. Run Deepak's pipeline first.",
        )

    return data


@router.get("/api/deepak-water")
def deepak_water_analysis():
    data = load_deepak_water_analysis()

    if not data["history"]:
        raise HTTPException(
            status_code=503,
            detail="Water Quality data is unavailable. Run Deepak's Water pipeline first.",
        )

    return data
