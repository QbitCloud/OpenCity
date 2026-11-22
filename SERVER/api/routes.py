from fastapi import APIRouter, HTTPException
from pymongo.errors import PyMongoError

from SERVER.services.hospitals import get_hospital_data
from SERVER.services.courts import get_court_data
from SERVER.services.schools import get_school_data

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
