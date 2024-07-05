<<<<<<< HEAD
from fastapi import FastAPI, Depends, HTTPException, Security
from fastapi.security import APIKeyHeader
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

db_user_name = os.environ.get("DB_USER_NAME")
db_password = os.environ.get("DB_PASSWORD")
db_host = os.environ.get("DB_HOST")
db_name = os.environ.get("DB_NAME")

SQLALCHEMY_DATABASE_URL = f'postgresql://{db_user_name}:{db_password}@{db_host}/{db_name}'
engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

class Client(Base):
    __tablename__ = "clients"

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
=======
from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from pydantic import BaseModel
import requests
from bs4 import BeautifulSoup
import time
import datetime
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
import random
from typing import List, Dict

app = FastAPI()
security = HTTPBasic()

class ReadingData(BaseModel):
    year: int
    month: int
    book_count: int
    chapter_count: int
    word_count: int
    daily_data: Dict[int, Dict[str, int]]

class ScraperResponse(BaseModel):
    data: List[ReadingData]

def get_session():
    session = requests.Session()
    retry = Retry(total=3, backoff_factor=0.1, status_forcelist=[500, 502, 503, 504])
    adapter = HTTPAdapter(max_retries=retry)
    session.mount('http://', adapter)
    session.mount('https://', adapter)
    return session

def get_random_user_agent():
    user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Safari/605.1.15",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36"
    ]
    return random.choice(user_agents)

def parse_count(text: str) -> int:
    return int(text.replace("\n", "").replace(" ", "").replace("\t", "").replace(",", "").replace("-", "0"))

def parse_daily_data(daily_table) -> Dict[int, Dict[str, int]]:
    daily_data = {}
    for row in daily_table:
        cells = row.find_all('td')
        if len(cells) < 4:
            continue
        day = int(cells[0].text[-2:])
        daily_data[day] = {
            'daily_book_count': parse_count(cells[1].text),
            'daily_chapter_count': parse_count(cells[2].text),
            'daily_word_count': parse_count(cells[3].text)
        }
    return daily_data

@app.post("/reading_data", response_model=ScraperResponse)
async def scrape_hameln(credentials: HTTPBasicCredentials = Depends(security)):
    userId = credentials.username
    password = credentials.password

    headers = {
        "User-Agent": get_random_user_agent(),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
    }

    login_url = "https://syosetu.org/"
    session = get_session()

    login_data = {
        "id": userId,
        "pass": password,
        "autologin": "1",
        "submit": "ログイン",
        "mode": "login_entry_end",
        "redirect_mode": ""
    }

    try:
        response = session.post(login_url, headers=headers, data=login_data, verify=True)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=401, detail=f"Login failed: {str(e)}")

    time.sleep(3)

    reading_data = []
    current_year = datetime.datetime.now().year
    current_month = datetime.datetime.now().month

    for year in range(2024, current_year + 1):
        for month in range(2, 13):
            if year == current_year and month > current_month:
                break

            history_url = f"https://syosetu.org/?mode=view_reading_history&type=&date={year}-{month}"
            
            try:
                response = session.get(history_url, headers=headers, verify=True)
                response.raise_for_status()
            except requests.exceptions.RequestException as e:
                print(f"Failed to fetch data for {year}-{month}: {str(e)}")
                continue

            soup = BeautifulSoup(response.text, "html.parser")
            table = soup.find('table', class_="table1")
            if not table:
                print(f"No data found for {year}-{month}")
                continue

            info = table.find_all("td")
            book_count = parse_count(info[0].get_text())
            chapter_count = parse_count(info[1].get_text())
            word_count = parse_count(info[2].get_text())

            daily_table = soup.find_all('table', class_='table1')
            if len(daily_table) < 4:
                print(f"Daily data not found for {year}-{month}")
                continue

            daily_table = daily_table[3].find_all('tr')[1:-1]
            daily_data = parse_daily_data(daily_table)

            reading_data.append(ReadingData(
                year=year,
                month=month,
                book_count=book_count,
                chapter_count=chapter_count,
                word_count=word_count,
                daily_data=daily_data
            ))

            time.sleep(3)

    return ScraperResponse(data=reading_data)
>>>>>>> refs/remotes/origin/main
