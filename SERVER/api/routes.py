from fastapi import APIRouter, HTTPException
from pymongo.errors import PyMongoError
from pydantic import BaseModel, Field

from SERVER.services.rti import generate_rti

from SERVER.services.hospitals import get_hospital_data
from SERVER.services.courts import get_court_data
from SERVER.services.schools import get_school_data
from SERVER.services.officials import get_officials_data
from SERVER.services.court_officials import get_court_officials_data

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
    try:
        data = load_deepak_finance_analysis()
    except PyMongoError:
        raise HTTPException(status_code=503, detail="Historic Finance database is unavailable")

    if not data["history"]:
        raise HTTPException(
            status_code=503,
            detail="Historic Finance data is unavailable. Run Deepak's pipeline first.",
        )

    return data


@router.get("/api/deepak-water")
def deepak_water_analysis():
    try:
        data = load_deepak_water_analysis()
    except PyMongoError:
        raise HTTPException(status_code=503, detail="Water Quality database is unavailable")

    if not data["history"]:
        raise HTTPException(
            status_code=503,
            detail="Water Quality data is unavailable. Run Deepak's Water pipeline first.",
        )

    return data

# SMC officials through the API
@router.get("/officials")
def officials():
    try:
        return get_officials_data()
    except PyMongoError:
        raise HTTPException(status_code=503, detail="Officials database is unavailable")


# Posts responsible for the court figures through the API
@router.get("/court-officials")
def court_officials():
    try:
        return get_court_officials_data()
    except PyMongoError:
        raise HTTPException(status_code=503, detail="Court officials database is unavailable")


# Data needed to generate an RTI query.
class RTIRequest(BaseModel):
    context: str = Field(min_length=1, max_length=400)


# Generate the RTI text using the local Ollama model.
@router.post("/rti/generate")
def rti_generate(request: RTIRequest):
    try:
        text = generate_rti(request.context)
        return {"text": text}
    except ValueError as error:
        raise HTTPException(status_code=502, detail=str(error))
    except Exception:
        raise HTTPException(status_code=503, detail="RTI generation is unavailable. Check Ollama and try again.")
