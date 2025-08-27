from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Optional

from models.database import get_db
from schemas.booking import BookingRequest, BookingResponse, BookingCreate
from schemas.common import ErrorResponse, SuccessResponse
from services.booking_service import BookingService

router = APIRouter()


@router.post("/", response_model=BookingResponse, status_code=status.HTTP_201_CREATED)
async def create_booking(
    booking_data: BookingCreate,
    db: Session = Depends(get_db)
):
    """
    Create a new booking with automatic return date calculation
    
    This endpoint validates the booking request, checks vehicle availability,
    calculates the return date based on business rules, and creates the booking.
    
    Business rules for return date:
    - If end date falls on Friday: return Monday 9:00 AM
    - If end date falls on weekend: return next Monday 9:00 AM
    - Otherwise: return at end_datetime
    """
    try:
        booking = BookingService.create_booking(db, booking_data)
        
        # Load vehicle information for response
        booking_dict = {
            "id": booking.id,
            "vehicle_id": booking.vehicle_id,
            "start_datetime": booking.start_datetime,
            "end_datetime": booking.end_datetime,
            "return_datetime": booking.return_datetime,
            "reason": booking.reason,
            "estimated_mileage": booking.estimated_mileage,
            "status": booking.status,
            "created_at": booking.created_at,
            "vehicle": {
                "id": booking.vehicle.id,
                "registration": booking.vehicle.registration,
                "make": booking.vehicle.make,
                "color": booking.vehicle.color
            } if booking.vehicle else None
        }
        
        return BookingResponse(**booking_dict)
        
    except ValueError as e:
        if "not found" in str(e):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=str(e)
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e)
            )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while creating the booking"
        )


@router.get("/{booking_id}", response_model=BookingResponse)
async def get_booking(
    booking_id: int,
    db: Session = Depends(get_db)
):
    """
    Get a booking by its ID
    
    Returns the booking details including vehicle information.
    """
    booking = BookingService.get_booking_by_id(db, booking_id)
    
    if not booking:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Booking with ID {booking_id} not found"
        )
    
    # Prepare response with vehicle information
    booking_dict = {
        "id": booking.id,
        "vehicle_id": booking.vehicle_id,
        "start_datetime": booking.start_datetime,
        "end_datetime": booking.end_datetime,
        "return_datetime": booking.return_datetime,
        "reason": booking.reason,
        "estimated_mileage": booking.estimated_mileage,
        "status": booking.status,
        "created_at": booking.created_at,
        "vehicle": {
            "id": booking.vehicle.id,
            "registration": booking.vehicle.registration,
            "make": booking.vehicle.make,
            "color": booking.vehicle.color
        } if booking.vehicle else None
    }
    
    return BookingResponse(**booking_dict)