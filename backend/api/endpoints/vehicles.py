from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List
from datetime import date

from models.database import get_db
from schemas.vehicle import VehicleResponse
from schemas.common import ErrorResponse
from services.vehicle_service import VehicleService

router = APIRouter()


@router.get("/", response_model=List[VehicleResponse])
async def get_all_vehicles(db: Session = Depends(get_db)):
    """
    Get all vehicles
    
    Returns:
        List of all vehicles with their details
    """
    try:
        vehicles = VehicleService.get_all_vehicles(db)
        return vehicles
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve vehicles: {str(e)}")


@router.get("/available", response_model=List[VehicleResponse])
async def get_available_vehicles(
    start_date: date = Query(..., description="Start date for availability check (YYYY-MM-DD)"),
    end_date: date = Query(..., description="End date for availability check (YYYY-MM-DD)"),
    db: Session = Depends(get_db)
):
    """
    Get available vehicles for a date range
    
    Args:
        start_date: Start date for availability check
        end_date: End date for availability check
        
    Returns:
        List of vehicles available for the specified date range
    """
    try:
        # Validate date range
        if start_date > end_date:
            raise HTTPException(status_code=400, detail="Start date must be before or equal to end date")
        
        # Check if start date is in the past
        if start_date < date.today():
            raise HTTPException(status_code=400, detail="Start date cannot be in the past")
        
        vehicles = VehicleService.get_available_vehicles(db, start_date, end_date)
        return vehicles
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve available vehicles: {str(e)}")