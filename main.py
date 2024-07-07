from fastapi import FastAPI, Depends, HTTPException, Security
from fastapi.security import APIKeyHeader
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from sqlalchemy import create_engine, Column, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from passlib.hash import argon2
from pydantic import BaseModel
from typing import Union
from services import *
from dotenv import load_dotenv
import os

load_dotenv()

db_url = os.environ.get("DATABASE_URL")

SQLALCHEMY_DATABASE_URL = f'postgresql://{db_url}'
engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

class Client(Base):
    __tablename__ = "sqdb"

    user_id = Column(String, primary_key=True, index=True)
    hashed_password = Column(String)

class ClientCreate(BaseModel):
    user_id: str
    password: str


Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Client Management and Reading Data API",
    description="This API provides endpoints for client registration and retrieving reading data.",
    version="1.0.0"
)

app.add_middleware(
    TrustedHostMiddleware, allowed_hosts=["hameln-reading-data.onrender.com"]
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)

@app.post("/register_client",
          summary="Register a new client",
          description="Register a new client with a user_id and password and they are used for logging to hameln. The password is hashed before storing.")
async def register_client(client: ClientCreate, db: Session = Depends(get_db)):
    existingClient = db.query(Client).filter(Client.user_id == client.user_id).first()
    if existingClient:
        raise HTTPException(status_code=400, detail="user_id already registered")

    hashed_password = argon2.hash(client.password)

    newClient = Client(user_id=client.user_id, hashed_password=hashed_password)
    db.add(newClient)
    db.commit()

    return {"message": "Client registered successfully"}

def verify_api_key(api_key: str = Security(api_key_header), db: Session = Depends(get_db)):
    if not api_key:
        raise HTTPException(status_code=403, detail="API Key is required")

    try:
        user_id, password = api_key.split(":")
    except ValueError:
        raise HTTPException(status_code=403, detail="Invalid API Key format")

    client = db.query(Client).filter(Client.user_id == user_id).first()
    if not client:
        raise HTTPException(status_code=403, detail="Invalid client ID")

    if not argon2.verify(password, client.hashed_password):
        raise HTTPException(status_code=403, detail="Invalid client secret")

    return [user_id, password]

@app.post("/get_reading_data",
          summary="Get reading data at hameln for a client",
          description="Retrieve reading data at hameln for an authenticated client. Requires a valid API key in the form \'user_id:password\'.")
async def get_reading_data(client: list = Depends(verify_api_key)):
    reading_data = scrape_hameln(client[0], client[1])
    return reading_data
