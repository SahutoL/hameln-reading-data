from fastapi import FastAPI
from app.routers import reading_data

app = FastAPI()

app.include_router(reading_data.router, prefix="/api/v1")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)