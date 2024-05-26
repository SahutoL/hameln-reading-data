from fastapi import APIRouter, Form, HTTPException
from app.services import login_and_get_reading_data

router = APIRouter()

@router.post("/reading_data")
def get_reading_data(userId: str = Form(...), password: str = Form(...)):
    try:
        reading_data = login_and_get_reading_data(userId, password)
        return reading_data
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))