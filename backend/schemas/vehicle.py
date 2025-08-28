from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class VehicleBase(BaseModel):
    registration: str = Field(..., min_length=1, max_length=20, description="Vehicle registration number")
    make: str = Field(..., min_length=1, max_length=50, description="Vehicle make/manufacturer")
    color: str = Field(..., min_length=1, max_length=30, description="Vehicle color")


class VehicleCreate(VehicleBase):
    """Schema for creating a new vehicle"""
    pass


class VehicleUpdate(BaseModel):
    """Schema for updating an existing vehicle"""
    registration: Optional[str] = Field(None, min_length=1, max_length=20)
    make: Optional[str] = Field(None, min_length=1, max_length=50)
    color: Optional[str] = Field(None, min_length=1, max_length=30)


class VehicleResponse(VehicleBase):
    """Schema for vehicle response"""
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True