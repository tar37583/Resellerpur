
from __future__ import annotations
from fastapi import FastAPI
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from agents.price_suggestor import PriceSuggestor
from agents.chat_moderation import ChatModerator
import os

DATA_PATH = os.environ.get("RESELLPUR_DATA", "data/listings.csv")

app = FastAPI(title="Resellpur Agents", version="1.0.0")

price_agent = PriceSuggestor.from_csv(DATA_PATH)
moderator = ChatModerator()

class PriceQuery(BaseModel):
    id: Optional[int] = None
    title: Optional[str] = None
    category: str
    brand: str
    condition: str = Field(pattern="^(Like New|Good|Fair)$")
    age_months: int
    asking_price: Optional[float] = None
    location: Optional[str] = None

class ModQuery(BaseModel):
    message: str

@app.post("/negotiate")
def negotiate(q: PriceQuery):
    suggestion = price_agent.suggest(q.dict())
    return {"input": q.dict(), "suggestion": suggestion}

@app.post("/moderate")
def moderate(q: ModQuery):
    result = moderator.moderate(q.message)
    return {"input": q.message, "result": result}

@app.get("/health")
def health():
    return {"status": "ok"}
