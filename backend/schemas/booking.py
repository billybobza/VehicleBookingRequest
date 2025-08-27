from pydantic import BaseModel, Field, field_validator, model_validator
from datetime import datetime
from typing import Optional


class BookingCreate(BaseModel):
    """Model for creating a new booking"""
    vehicle_id: int = Field(..., description="ID of the vehicle to book")
    start_datetime: datetime = Field(..., description="Start date and time of booking")
    end_datetime: datetime = Field(..., description="End date and time of booking")
    reason: str = Field(..., min_length=1, max_length=500, description="Reason for booking")
    estimated_mileage: int = Field(..., ge=0, le=10000, description="Estimated mileage for the trip")
    
    @field_validator('start_datetime')
    @classmethod
    def start_not_in_past(cls, v):
        if v < datetime.now():
            raise ValueError('Start datetime cannot be in the past')
        return v
    
    @model_validator(mode='after')
    def end_after_start(self):
        if self.end_datetime <= self.start_datetime:
            raise ValueError('End datetime must be after start datetime')
        return self


class BookingRequest(BookingCreate):
    """Request model for booking (extends BookingCreate)"""
    pass


class BookingResponse(BaseModel):
    """Response model for booking data"""
    id: int
    vehicle_id: int
    start_datetime: datetime
    end_datetime: datetime
    return_datetime: datetime
    reason: str
    estimated_mileage: int
    status: str
    created_at: datetime
    
    # Include vehicle information
    vehicle: Optional[dict] = None
    
    model_config = {"from_attributes": True}