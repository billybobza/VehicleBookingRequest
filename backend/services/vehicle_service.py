from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from typing import List
from datetime import date, datetime

from models.database import Vehicle, Booking, VehicleAvailability


class VehicleService:
    """Service class for vehicle-related business logic"""
    
    @staticmethod
    def get_all_vehicles(db: Session) -> List[Vehicle]:
        """
        Get all vehicles from the database
        
        Args:
            db: Database session
            
        Returns:
            List of all vehicles
        """
        return db.query(Vehicle).all()
    
    @staticmethod
    def get_available_vehicles(db: Session, start_date: date, end_date: date) -> List[Vehicle]:
        """
        Get vehicles that are available for the specified date range
        
        Args:
            db: Database session
            start_date: Start date for availability check
            end_date: End date for availability check
            
        Returns:
            List of available vehicles
        """
        # Get all vehicles
        all_vehicles = db.query(Vehicle).all()
        available_vehicles = []
        
        for vehicle in all_vehicles:
            if VehicleService._is_vehicle_available(db, vehicle.id, start_date, end_date):
                available_vehicles.append(vehicle)
        
        return available_vehicles
    
    @staticmethod
    def _is_vehicle_available(db: Session, vehicle_id: int, start_date: date, end_date: date) -> bool:
        """
        Check if a specific vehicle is available for the given date range
        
        Args:
            db: Database session
            vehicle_id: ID of the vehicle to check
            start_date: Start date for availability check
            end_date: End date for availability check
            
        Returns:
            True if vehicle is available, False otherwise
        """
        # Convert dates to datetime for comparison with bookings
        start_datetime = datetime.combine(start_date, datetime.min.time())
        end_datetime = datetime.combine(end_date, datetime.max.time())
        
        # Check for overlapping bookings
        overlapping_bookings = db.query(Booking).filter(
            and_(
                Booking.vehicle_id == vehicle_id,
                Booking.status == "confirmed",
                # Check for overlap: booking starts before our end AND booking ends after our start
                Booking.start_datetime < end_datetime,
                Booking.end_datetime > start_datetime
            )
        ).first()
        
        # If there are overlapping bookings, vehicle is not available
        if overlapping_bookings:
            return False
        
        # Check availability records (seed data)
        # Vehicle is available if there's at least one availability record that covers the entire period
        availability_records = db.query(VehicleAvailability).filter(
            and_(
                VehicleAvailability.vehicle_id == vehicle_id,
                VehicleAvailability.is_available == True,
                VehicleAvailability.start_date <= start_date,
                VehicleAvailability.end_date >= end_date
            )
        ).first()
        
        # If no availability record covers the entire period, check if there are any unavailable periods
        if not availability_records:
            # Check if there are any unavailable periods that overlap with our request
            unavailable_records = db.query(VehicleAvailability).filter(
                and_(
                    VehicleAvailability.vehicle_id == vehicle_id,
                    VehicleAvailability.is_available == False,
                    # Check for overlap
                    VehicleAvailability.start_date <= end_date,
                    VehicleAvailability.end_date >= start_date
                )
            ).first()
            
            # If there are unavailable periods overlapping, vehicle is not available
            if unavailable_records:
                return False
            
            # If no specific availability or unavailability records, assume available
            return True
        
        return True