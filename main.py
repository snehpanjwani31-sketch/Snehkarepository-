from datetime import datetime
from enum import Enum
from typing import Dict, Optional
from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, Field

app = FastAPI(
    title="Match Scoreboard API",
    description="A simple API to track and update live match scores.",
    version="1.0.0",
)


# --- Models & Enums ---
class MatchStatus(str, Enum):
    SCHEDULED = "scheduled"
    LIVE = "live"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class MatchCreate(BaseModel):
    team_a: str = Field(..., min_length=1, max_length=100, example="Team Red")
    team_b: str = Field(..., min_length=1, max_length=100, example="Team Blue")
    sport: str = Field(..., min_length=2, max_length=50, example="Football")


class ScoreUpdate(BaseModel):
    score_a: Optional[int] = Field(None, ge=0, example=2)
    score_b: Optional[int] = Field(None, ge=0, example=1)
    status: Optional[MatchStatus] = Field(None, example=MatchStatus.LIVE)
    additional_info: Optional[str] = Field(
        None, max_length=255, example="Half-time"
    )


class MatchResponse(BaseModel):
    match_id: int
    team_a: str
    team_b: str
    score_a: int
    score_b: int
    sport: str
    status: MatchStatus
    additional_info: Optional[str]
    last_updated: datetime


# --- In-Memory Database ---
# Using a dictionary to mock a database for quick testing
db_matches: Dict[int, dict] = {}
match_id_counter = 1


# --- API Endpoints ---


@app.post(
    "/matches",
    response_model=MatchResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_match(match_data: MatchCreate):
    """Creates a new match with default scores set to 0."""
    global match_id_counter

    new_match = {
        "match_id": match_id_counter,
        "team_a": match_data.team_a,
        "team_b": match_data.team_b,
        "score_a": 0,
        "score_b": 0,
        "sport": match_data.sport,
        "status": MatchStatus.SCHEDULED,
        "additional_info": "Match not started yet.",
        "last_updated": datetime.utcnow(),
    }

    db_matches[match_id_counter] = new_match
    match_id_counter += 1
    return new_match


@app.get("/matches", response_model=Dict[str, list])
def get_all_matches():
    """Retrieves all registered matches."""
    return {"matches": list(db_matches.values())}


@app.get("/matches/{match_id}", response_model=MatchResponse)
def get_match_by_id(match_id: int):
    """Retrieves the live scoreboard data for a single match."""
    if match_id not in db_matches:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Match with ID {match_id} not found",
        )
    return db_matches[match_id]


@app.patch("/matches/{match_id}", response_model=MatchResponse)
def update_score(match_id: int, updates: ScoreUpdate):
    """Updates scores, match status, or extra commentary details."""
    if match_id not in db_matches:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Match with ID {match_id} not found",
        )

    match = db_matches[match_id]

    # Dynamically apply only the fields provided in the request payload
    update_data = updates.dict(exclude_unset=True)

    if not update_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No valid fields provided for update.",
        )

    for key, value in update_data.items():
        match[key] = value

    match["last_updated"] = datetime.utcnow()
    db_matches[match_id] = match

    return match


@app.delete("/matches/{match_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_match(match_id: int):
    """Deletes a match from the scoreboard system."""
    if match_id not in db_matches:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Match with ID {match_id} not found",
        )
    del db_matches[match_id]
    return None
