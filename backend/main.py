from fastapi import FastAPI, Request, Depends
from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from datetime import datetime
import os
from dotenv import load_dotenv
import requests

load_dotenv()

HUGGINGFACE_API_URL = "https://api-inference.huggingface.co/models/facebook/blenderbot-400M-distill"
HUGGINGFACE_TOKEN = os.getenv("HUGGINGFACE_TOKEN")
headers = {"Authorization": f"Bearer {HUGGINGFACE_TOKEN}"}

DATABASE_URL = os.getenv("DATABASE")
engine = create_engine (DATABASE_URL, connect_args={"ssl_disabled": True})

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

class UserMessage(Base):
    __tablename__ = "plannerassistant"
    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow())
    message = Column(String(1000), index=True)
    response = Column(String(2000))

app = FastAPI()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/plan")
async def get_plan(request: Request, db: Session = Depends(get_db)):
    data = await request.json()
    message = data.get("message", "")

    payload = {"inputs": message}
    response = requests.post(HUGGINGFACE_API_URL, headers=headers, json=payload)

    if response.status_code == 200:
        response = response.json()[0]['generated_text']
    else:
        response = "Currently unavailable. Please try again later."

    db_message = UserMessage(
        message = message,
        response = response
    )
    db.add(db_message)
    db.commit()
    db.refresh(db_message)

    return {"response": response}

@app.get("/")
def read_root():
    return {"message": "Hello, World! Welcome to the Plan Your Day Bot!"}
