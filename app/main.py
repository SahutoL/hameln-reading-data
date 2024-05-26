from fastapi import FastAPI
from app.routers import reading_data

app = FastAPI()

app.include_router(reading_data.router, prefix="/api/v1")
