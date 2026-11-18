from fastapi import APIRouter, HTTPException
from pymongo.errors import PyMongoError

from SERVER.services.courts import get_court_data
from SERVER.services.schools import get_school_data

router = APIRouter()


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
