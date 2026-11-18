from fastapi import APIRouter, HTTPException
from pymongo.errors import PyMongoError
from pydantic import BaseModel, Field

from SERVER.services.rti import generate_rti

from SERVER.services.schools import get_school_data
from SERVER.services.officials import get_officials_data

router = APIRouter()


# Return school data through the API
@router.get("/schools")
def schools():
    try:
        school_data = get_school_data()
        return school_data
    except PyMongoError:
        raise HTTPException(status_code=503, detail="School database is unavailable")


# SMC officials through the API
@router.get("/officials")
def officials():
    try:
        return get_officials_data()
    except PyMongoError:
        raise HTTPException(status_code=503, detail="Officials database is unavailable")


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
