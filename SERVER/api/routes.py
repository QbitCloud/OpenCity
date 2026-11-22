from fastapi import APIRouter, HTTPException
from pymongo.errors import PyMongoError

from SERVER.services.hospitals import get_hospital_data
from SERVER.services.courts import get_court_data
from SERVER.services.schools import get_school_data

from SERVER.services.deepak_finance import load_deepak_finance_analysis
from SERVER.services.deepak_water import load_deepak_water_analysis
from SERVER.services.finance import load_finance_summary

router = APIRouter()


# Return hospital data through the API
@router.get("/hospitals")
def hospitals():
    try:
        hospital_data = get_hospital_data()
        return hospital_data
    except PyMongoError:
        raise HTTPException(status_code=503, detail="Hospital database is unavailable")
# Return court data through the API
@router.get("/courts")
def courts():
    try:
        court_data = get_court_data()
        return court_data
    except PyMongoError:
        raise HTTPException(status_code=503, detail="Court database is unavailable")
# Return school data through the API
@router.get("/schools")
def schools():
    try:
        school_data = get_school_data()
        return school_data
    except PyMongoError:
        raise HTTPException(status_code=503, detail="School database is unavailable")

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
