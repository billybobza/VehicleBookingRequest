from pydantic import BaseModel, Field
from datetime import datetime, date
from typing import Optional


class VehicleResponse(BaseModel):
    """Response model for vehicle data"""
    id: int
    registration: str
    make: str
    color: str
    created_at: datetime
    updated_at: datetime
    
    model_config = {"from_attributes": True}