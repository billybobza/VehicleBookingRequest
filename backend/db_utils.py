#!/usr/bin/env python3
"""
Database utility functions for the car booking system
"""

from datetime import datetime, date, timedelta
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_

from models.database import SessionLocal, Vehicle, Booking, VehicleAvailability


def get_all_vehicles(db: Session) -> List[Vehicle]:
    """Get all vehicles from the database"""
    return db.query(Vehicle).all()


def get_vehicle_by_id(db: Session, vehicle_id: int) -> Optional[Vehicle]:
    """Get a vehicle by its ID"""
    return db.query(Vehicle).filter(Vehicle.id == vehicle_id).first()


def get_vehicle_by_registration(db: Session, registration: str) -> Optional[Vehicle]:
    """Get a vehicle by its registration number"""
    return db.query(Vehicle).filter(Vehicle.registration == registration).first()


def check_vehicle_availability(db: Session, vehicle_id: int, start_date: date, end_date: date) -> bool:
    """
    Check if a vehicle is available for the given date range
    Returns True if available, False if not available or has conflicts
    """
    # Check for existing bookings that overlap with the requested period
    overlapping_bookings = db.query(Booking).filter(
        and_(
            Booking.vehicle_id == vehicle_id,
            Booking.status == "confirmed",
            or_(
                # Booking starts during requested period
                and_(
                    Booking.start_datetime >= datetime.combine(start_date, datetime.min.time()),
                    Booking.start_datetime <= datetime.combine(end_date, datetime.max.time())
                ),
                # Booking ends during requested period
                and_(
                    Booking.end_datetime >= datetime.combine(start_date, datetime.min.time()),
                    Booking.end_datetime <= datetime.combine(end_date, datetime.max.time())
                ),
                # Booking spans the entire requested period
                and_(
                    Booking.start_datetime <= datetime.combine(start_date, datetime.min.time()),
                    Booking.end_datetime >= datetime.combine(end_date, datetime.max.time())
                )
            )
        )
    ).first()
    
    if overlapping_bookings:
        return False
    
    # Check availability records
    unavailable_periods = db.query(VehicleAvailability).filter(
        and_(
            VehicleAvailability.vehicle_id == vehicle_id,
            VehicleAvailability.is_available == False,
            or_(
                # Unavailable period overlaps with start of requested period
                and_(
                    VehicleAvailability.start_date <= start_date,
                    VehicleAvailability.end_date >= start_date
                ),
                # Unavailable period overlaps with end of requested period
                and_(
                    VehicleAvailability.start_date <= end_date,
                    VehicleAvailability.end_date >= end_date
                ),
                # Unavailable period is within requested period
                and_(
                    VehicleAvailability.start_date >= start_date,
                    VehicleAvailability.end_date <= end_date
                )
            )
        )
    ).first()
    
    return unavailable_periods is None


def get_available_vehicles(db: Session, start_date: date, end_date: date) -> List[Vehicle]:
    """Get all vehicles that are available for the given date range"""
    all_vehicles = get_all_vehicles(db)
    available_vehicles = []
    
    for vehicle in all_vehicles:
        if check_vehicle_availability(db, vehicle.id, start_date, end_date):
            available_vehicles.append(vehicle)
    
    return available_vehicles


def create_booking(
    db: Session,
    vehicle_id: int,
    start_datetime: datetime,
    end_datetime: datetime,
    return_datetime: datetime,
    reason: str,
    estimated_mileage: int
) -> Booking:
    """Create a new booking"""
    booking = Booking(
        vehicle_id=vehicle_id,
        start_datetime=start_datetime,
        end_datetime=end_datetime,
        return_datetime=return_datetime,
        reason=reason,
        estimated_mileage=estimated_mileage,
        status="confirmed"
    )
    
    db.add(booking)
    db.commit()
    db.refresh(booking)
    
    return booking


def get_booking_by_id(db: Session, booking_id: int) -> Optional[Booking]:
    """Get a booking by its ID"""
    return db.query(Booking).filter(Booking.id == booking_id).first()


def calculate_return_date(end_datetime: datetime) -> datetime:
    """
    Calculate return date based on business rules:
    - If end date falls on Friday: return Monday 9:00 AM
    - If end date falls on weekend: return next Monday 9:00 AM
    - Otherwise: return at end_datetime
    """
    end_date = end_datetime.date()
    
    # Check if it's Friday (weekday 4) or weekend (5=Saturday, 6=Sunday)
    if end_date.weekday() >= 4:  # Friday, Saturday, or Sunday
        # Find next Monday
        days_until_monday = (7 - end_date.weekday()) % 7
        if days_until_monday == 0:  # If it's already Monday
            days_until_monday = 7
        
        next_monday = end_date + timedelta(days=days_until_monday)
        return datetime.combine(next_monday, datetime.min.time().replace(hour=9))
    
    return end_datetime


# Context manager for database sessions
class DatabaseSession:
    """Context manager for database sessions"""
    
    def __enter__(self) -> Session:
        self.db = SessionLocal()
        return self.db
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type:
            self.db.rollback()
        self.db.close()


if __name__ == "__main__":
    # Example usage
    with DatabaseSession() as db:
        vehicles = get_all_vehicles(db)
        print(f"Found {len(vehicles)} vehicles")
        
        if vehicles:
            # Test availability check
            today = date.today()
            tomorrow = today + timedelta(days=1)
            
            available = get_available_vehicles(db, today, tomorrow)
            print(f"Available vehicles for {today} to {tomorrow}: {len(available)}")
            
            # Test return date calculation
            test_datetime = datetime.now()
            return_date = calculate_return_date(test_datetime)
            print(f"Return date for {test_datetime}: {return_date}")