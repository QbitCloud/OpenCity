from fastapi import APIRouter, HTTPException
from pymongo.errors import PyMongoError

from SERVER.services.hospitals import get_hospital_data

router = APIRouter()


# Return hospital data through the API
@router.get("/hospitals")
def hospitals():
    try:
        hospital_data = get_hospital_data()
        return hospital_data
    except PyMongoError:
        raise HTTPException(status_code=503, detail="Hospital database is unavailable")
