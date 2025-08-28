from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date

from models.database import get_db, Vehicle, Booking, VehicleAvailability
from schemas.vehicle import VehicleCreate, VehicleUpdate, VehicleResponse
from schemas.booking import BookingResponse
from services.vehicle_service import VehicleService
from services.booking_service import BookingService

router = APIRouter(prefix="/admin", tags=["admin"])


# Vehicle Management Endpoints
@router.get("/vehicles/", response_model=List[VehicleResponse])
def get_all_vehicles_admin(db: Session = Depends(get_db)):
    """Get all vehicles for admin management"""
    vehicles = VehicleService.get_all_vehicles(db)
    return vehicles


@router.post("/vehicles/", response_model=VehicleResponse, status_code=201)
def create_vehicle(vehicle_data: VehicleCreate, db: Session = Depends(get_db)):
    """Create a new vehicle"""
    # Check if registration already exists
    existing_vehicle = db.query(Vehicle).filter(Vehicle.registration == vehicle_data.registration).first()
    if existing_vehicle:
        raise HTTPException(status_code=400, detail="Vehicle with this registration already exists")
    
    vehicle = Vehicle(
        registration=vehicle_data.registration,
        make=vehicle_data.make,
        color=vehicle_data.color
    )
    
    db.add(vehicle)
    db.commit()
    db.refresh(vehicle)
    
    return vehicle


@router.put("/vehicles/{vehicle_id}", response_model=VehicleResponse)
def update_vehicle(vehicle_id: int, vehicle_data: VehicleUpdate, db: Session = Depends(get_db)):
    """Update an existing vehicle"""
    vehicle = db.query(Vehicle).filter(Vehicle.id == vehicle_id).first()
    if not vehicle:
        raise HTTPException(status_code=404, detail="Vehicle not found")
    
    # Check if new registration conflicts with existing vehicle
    if vehicle_data.registration and vehicle_data.registration != vehicle.registration:
        existing_vehicle = db.query(Vehicle).filter(
            Vehicle.registration == vehicle_data.registration,
            Vehicle.id != vehicle_id
        ).first()
        if existing_vehicle:
            raise HTTPException(status_code=400, detail="Vehicle with this registration already exists")
    
    # Update fields
    if vehicle_data.registration:
        vehicle.registration = vehicle_data.registration
    if vehicle_data.make:
        vehicle.make = vehicle_data.make
    if vehicle_data.color:
        vehicle.color = vehicle_data.color
    
    db.commit()
    db.refresh(vehicle)
    
    return vehicle


@router.delete("/vehicles/{vehicle_id}")
def delete_vehicle(vehicle_id: int, db: Session = Depends(get_db)):
    """Delete a vehicle"""
    vehicle = db.query(Vehicle).filter(Vehicle.id == vehicle_id).first()
    if not vehicle:
        raise HTTPException(status_code=404, detail="Vehicle not found")
    
    # Check if vehicle has active bookings
    active_bookings = db.query(Booking).filter(
        Booking.vehicle_id == vehicle_id,
        Booking.status == "confirmed"
    ).first()
    
    if active_bookings:
        raise HTTPException(
            status_code=400, 
            detail="Cannot delete vehicle with active bookings. Cancel bookings first."
        )
    
    db.delete(vehicle)
    db.commit()
    
    return {"message": "Vehicle deleted successfully"}


@router.post("/vehicles/{vehicle_id}/offline")
def take_vehicle_offline(
    vehicle_id: int, 
    start_date: date,
    end_date: date,
    reason: str,
    db: Session = Depends(get_db)
):
    """Take a vehicle offline for maintenance/service"""
    vehicle = db.query(Vehicle).filter(Vehicle.id == vehicle_id).first()
    if not vehicle:
        raise HTTPException(status_code=404, detail="Vehicle not found")
    
    if start_date > end_date:
        raise HTTPException(status_code=400, detail="Start date must be before or equal to end date")
    
    # Create unavailability record
    unavailability = VehicleAvailability(
        vehicle_id=vehicle_id,
        start_date=start_date,
        end_date=end_date,
        is_available=False,
        reason=reason  # We'll need to add this field to the model
    )
    
    db.add(unavailability)
    db.commit()
    
    return {"message": f"Vehicle {vehicle.registration} taken offline from {start_date} to {end_date}"}


@router.post("/vehicles/{vehicle_id}/online")
def bring_vehicle_online(vehicle_id: int, db: Session = Depends(get_db)):
    """Bring a vehicle back online"""
    vehicle = db.query(Vehicle).filter(Vehicle.id == vehicle_id).first()
    if not vehicle:
        raise HTTPException(status_code=404, detail="Vehicle not found")
    
    # Remove current unavailability records
    today = date.today()
    db.query(VehicleAvailability).filter(
        VehicleAvailability.vehicle_id == vehicle_id,
        VehicleAvailability.is_available == False,
        VehicleAvailability.end_date >= today
    ).delete()
    
    db.commit()
    
    return {"message": f"Vehicle {vehicle.registration} brought back online"}


# Booking Management Endpoints
@router.get("/bookings/", response_model=List[BookingResponse])
def get_all_bookings_admin(
    status: Optional[str] = None,
    vehicle_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """Get all bookings for admin management with optional filters"""
    query = db.query(Booking)
    
    if status:
        query = query.filter(Booking.status == status)
    
    if vehicle_id:
        query = query.filter(Booking.vehicle_id == vehicle_id)
    
    bookings = query.order_by(Booking.created_at.desc()).all()
    return bookings


@router.put("/bookings/{booking_id}/status")
def update_booking_status(
    booking_id: int, 
    status: str,
    db: Session = Depends(get_db)
):
    """Update booking status (approve, cancel, etc.)"""
    valid_statuses = ["confirmed", "cancelled", "completed", "pending"]
    if status not in valid_statuses:
        raise HTTPException(
            status_code=400, 
            detail=f"Invalid status. Must be one of: {', '.join(valid_statuses)}"
        )
    
    booking = db.query(Booking).filter(Booking.id == booking_id).first()
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    
    booking.status = status
    db.commit()
    db.refresh(booking)
    
    return {"message": f"Booking {booking_id} status updated to {status}", "booking": booking}


@router.delete("/bookings/{booking_id}")
def delete_booking(booking_id: int, db: Session = Depends(get_db)):
    """Delete a booking"""
    booking = db.query(Booking).filter(Booking.id == booking_id).first()
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    
    db.delete(booking)
    db.commit()
    
    return {"message": "Booking deleted successfully"}


# Vehicle Availability Management
@router.get("/vehicles/{vehicle_id}/availability")
def get_vehicle_availability(vehicle_id: int, db: Session = Depends(get_db)):
    """Get availability records for a specific vehicle"""
    vehicle = db.query(Vehicle).filter(Vehicle.id == vehicle_id).first()
    if not vehicle:
        raise HTTPException(status_code=404, detail="Vehicle not found")
    
    availability_records = db.query(VehicleAvailability).filter(
        VehicleAvailability.vehicle_id == vehicle_id
    ).order_by(VehicleAvailability.start_date).all()
    
    return {
        "vehicle": vehicle,
        "availability_records": availability_records
    }


@router.get("/dashboard/stats")
def get_admin_dashboard_stats(db: Session = Depends(get_db)):
    """Get dashboard statistics for admin"""
    total_vehicles = db.query(Vehicle).count()
    total_bookings = db.query(Booking).count()
    active_bookings = db.query(Booking).filter(Booking.status == "confirmed").count()
    pending_bookings = db.query(Booking).filter(Booking.status == "pending").count()
    
    # Vehicles currently offline
    today = date.today()
    offline_vehicles = db.query(VehicleAvailability).filter(
        VehicleAvailability.is_available == False,
        VehicleAvailability.start_date <= today,
        VehicleAvailability.end_date >= today
    ).count()
    
    return {
        "total_vehicles": total_vehicles,
        "total_bookings": total_bookings,
        "active_bookings": active_bookings,
        "pending_bookings": pending_bookings,
        "offline_vehicles": offline_vehicles,
        "available_vehicles": total_vehicles - offline_vehicles
    }