# main.py
from typing import Dict
from fastapi import FastAPI, status
from models import MatchCreate, MatchResponse, ScoreUpdate
from services import match_service

app = FastAPI(title="Match Scoreboard API")

@app.post("/matches", response_model=MatchResponse, status_code=status.HTTP_201_CREATED)
def create_match(match_data: MatchCreate):
    return match_service.create_match(match_data)

@app.get("/matches", response_model=Dict[str, list])
def get_all_matches():
    return {"matches": match_service.get_all_matches()}

@app.get("/matches/{match_id}", response_model=MatchResponse)
def get_match_by_id(match_id: int):
    return match_service.get_match_by_id(match_id)

@app.patch("/matches/{match_id}", response_model=MatchResponse)
def update_score(match_id: int, updates: ScoreUpdate):
    return match_service.update_score(match_id, updates)

@app.delete("/matches/{match_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_match(match_id: int):
    match_service.delete_match(match_id)
    return None
