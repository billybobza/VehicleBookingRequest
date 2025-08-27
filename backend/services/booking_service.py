from sqlalchemy.orm import Session
from sqlalchemy import and_
from typing import Optional
from datetime import datetime, date, timedelta

from models.database import Booking, Vehicle
from schemas.booking import BookingCreate


class BookingService:
    """Service class for booking-related business logic"""
    
    @staticmethod
    def create_booking(db: Session, booking_data: BookingCreate) -> Booking:
        """
        Create a new booking with automatic return date calculation
        
        Args:
            db: Database session
            booking_data: Booking creation data
            
        Returns:
            Created booking object
            
        Raises:
            ValueError: If vehicle is not available or doesn't exist
        """
        # Verify vehicle exists
        vehicle = db.query(Vehicle).filter(Vehicle.id == booking_data.vehicle_id).first()
        if not vehicle:
            raise ValueError(f"Vehicle with ID {booking_data.vehicle_id} not found")
        
        # Check if vehicle is available for the requested period
        if not BookingService._is_vehicle_available_for_booking(
            db, booking_data.vehicle_id, booking_data.start_datetime, booking_data.end_datetime
        ):
            raise ValueError("Vehicle is not available for the requested time period")
        
        # Calculate return date based on business rules
        return_datetime = BookingService.calculate_return_date(booking_data.end_datetime)
        
        # Create booking
        booking = Booking(
            vehicle_id=booking_data.vehicle_id,
            start_datetime=booking_data.start_datetime,
            end_datetime=booking_data.end_datetime,
            return_datetime=return_datetime,
            reason=booking_data.reason,
            estimated_mileage=booking_data.estimated_mileage,
            status="confirmed"
        )
        
        db.add(booking)
        db.commit()
        db.refresh(booking)
        
        return booking
    
    @staticmethod
    def get_booking_by_id(db: Session, booking_id: int) -> Optional[Booking]:
        """
        Get a booking by its ID
        
        Args:
            db: Database session
            booking_id: ID of the booking to retrieve
            
        Returns:
            Booking object if found, None otherwise
        """
        return db.query(Booking).filter(Booking.id == booking_id).first()
    
    @staticmethod
    def calculate_return_date(end_datetime: datetime) -> datetime:
        """
        Calculate return date based on business rules:
        - If end date falls on Friday: return Monday 9:00 AM
        - If end date falls on weekend: return next Monday 9:00 AM
        - Otherwise: return at end_datetime
        
        Args:
            end_datetime: The end datetime of the booking
            
        Returns:
            Calculated return datetime
        """
        end_date = end_datetime.date()
        weekday = end_date.weekday()  # Monday=0, Sunday=6
        
        # If Friday (4) or weekend (5=Saturday, 6=Sunday)
        if weekday >= 4:
            # Calculate next Monday
            days_until_monday = (7 - weekday) % 7
            if days_until_monday == 0:  # If it's already Monday
                days_until_monday = 7
            
            next_monday = end_date + timedelta(days=days_until_monday)
            return datetime.combine(next_monday, datetime.min.time().replace(hour=9))
        else:
            # Return at the original end datetime
            return end_datetime
    
    @staticmethod
    def _is_vehicle_available_for_booking(
        db: Session, 
        vehicle_id: int, 
        start_datetime: datetime, 
        end_datetime: datetime
    ) -> bool:
        """
        Check if a vehicle is available for booking during the specified period
        
        Args:
            db: Database session
            vehicle_id: ID of the vehicle to check
            start_datetime: Start datetime of the booking
            end_datetime: End datetime of the booking
            
        Returns:
            True if available, False otherwise
        """
        # Check for overlapping confirmed bookings
        overlapping_bookings = db.query(Booking).filter(
            and_(
                Booking.vehicle_id == vehicle_id,
                Booking.status == "confirmed",
                # Check for overlap: booking starts before our end AND booking ends after our start
                Booking.start_datetime < end_datetime,
                Booking.end_datetime > start_datetime
            )
        ).first()
        
        return overlapping_bookings is None