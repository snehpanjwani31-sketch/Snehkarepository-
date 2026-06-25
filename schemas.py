from datetime import datetime
from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field, field_validator


# --- Enums ---
class MatchStatus(str, Enum):
    SCHEDULED = "scheduled"
    LIVE = "live"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


# --- Match Base Model ---
class MatchBase(BaseModel):
    """Core properties shared across creation, updates, and responses."""

    team_a: str = Field(..., min_length=1, max_length=100, json_schema_extra={"example": "India"})
    team_b: str = Field(..., min_length=1, max_length=100, json_schema_extra={"example": "Australia"})
    match_format: str = Field("T20", description="T20, ODI, or Test", json_schema_extra={"example": "T20"})
    venue: Optional[str] = Field(None, max_length=150, json_schema_extra={"example": "Wankhede Stadium"})


# --- Match Create Model ---
class MatchCreate(MatchBase):
    """Schema for initializing a new cricket match. Inherits base fields."""
    
    # Defaults all starting metrics to 0 upon match creation
    runs_a: int = Field(0, ge=0)
    wickets_a: int = Field(0, ge=0, le=10)
    overs_a: float = Field(0.0, ge=0.0)
    
    runs_b: int = Field(0, ge=0)
    wickets_b: int = Field(0, ge=0, le=10)
    overs_b: float = Field(0.0, ge=0.0)
    
    target: Optional[int] = Field(None, ge=1, description="Target runs for the team batting second")


# --- Match Update Model ---
class MatchUpdate(BaseModel):
    """Schema for validating partial live score, wicket, and over updates."""

    runs_a: Optional[int] = Field(None, ge=0, description="Current runs scored by Team A")
    wickets_a: Optional[int] = Field(None, ge=0, le=10, description="Wickets lost by Team A")
    overs_a: Optional[float] = Field(None, ge=0.0, description="Overs bowled to Team A (e.g., 14.5)")
    
    runs_b: Optional[int] = Field(None, ge=0, description="Current runs scored by Team B")
    wickets_b: Optional[int] = Field(None, ge=0, le=10, description="Wickets lost by Team B")
    overs_b: Optional[float] = Field(None, ge=0.0, description="Overs bowled to Team B (e.g., 5.2)")
    
    target: Optional[int] = Field(None, ge=1, description="Update or set target runs")
    status: Optional[MatchStatus] = Field(None, json_schema_extra={"example": MatchStatus.LIVE})
    additional_info: Optional[str] = Field(
        None, max_length=255, description="Live commentary commentary line", json_schema_extra={"example": "Rain stops play."}
    )

    @field_validator("overs_a", "overs_b")
    @classmethod
    def validate_cricket_overs(cls, value: Optional[float]) -> Optional[float]:
        """Validates that cricket overs cannot have a decimal part greater than .5"""
        if value is not None:
            # Extract the fractional ball part (e.g., 14.5 -> 0.5)
            balls = round(value - int(value), 1)
            if balls > 0.5:
                raise ValueError("Overs decimal part cannot exceed .5 (e.g., 5.5 is valid, 5.6 is invalid)")
        return value


# --- Response Models (Data Output) ---
class MatchResponse(MatchBase):
    """Schema defining the complete structured output for a cricket match scoreboard."""

    match_id: int
    runs_a: int
    wickets_a: int
    overs_a: float
    runs_b: int
    wickets_b: int
    overs_b: float
    target: Optional[int]
    status: MatchStatus
    additional_info: Optional[str]
    last_updated: datetime

    class Config:
        from_attributes = True


class MatchListResponse(BaseModel):
    """Schema for displaying a clean collection of multiple live cricket matches."""

    matches: List[MatchResponse]
