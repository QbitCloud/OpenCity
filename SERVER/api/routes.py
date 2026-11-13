from fastapi import APIRouter, HTTPException
from pymongo.errors import PyMongoError

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
