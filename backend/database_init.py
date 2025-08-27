import random
from datetime import datetime, date, timedelta
from sqlalchemy.orm import Session
from models.database import engine, SessionLocal, create_tables, Vehicle, VehicleAvailability


def seed_vehicles(db: Session) -> None:
    """Seed the database with 11 company vehicles"""
    
    # Check if vehicles already exist
    existing_count = db.query(Vehicle).count()
    if existing_count > 0:
        print(f"Vehicles already exist ({existing_count} found). Skipping vehicle seeding.")
        return
    
    # Vehicle data - 11 company vehicles with realistic registrations, makes, and colors
    vehicles_data = [
        {"registration": "ABC123", "make": "Toyota", "color": "White"},
        {"registration": "DEF456", "make": "Honda", "color": "Silver"},
        {"registration": "GHI789", "make": "Ford", "color": "Blue"},
        {"registration": "JKL012", "make": "Volkswagen", "color": "Black"},
        {"registration": "MNO345", "make": "Nissan", "color": "Red"},
        {"registration": "PQR678", "make": "Hyundai", "color": "Gray"},
        {"registration": "STU901", "make": "Mazda", "color": "White"},
        {"registration": "VWX234", "make": "Subaru", "color": "Blue"},
        {"registration": "YZA567", "make": "Kia", "color": "Silver"},
        {"registration": "BCD890", "make": "Mitsubishi", "color": "Black"},
        {"registration": "EFG123", "make": "Suzuki", "color": "Green"}
    ]
    
    # Create vehicle records
    vehicles = []
    for vehicle_data in vehicles_data:
        vehicle = Vehicle(**vehicle_data)
        vehicles.append(vehicle)
        db.add(vehicle)
    
    db.commit()
    print(f"Successfully seeded {len(vehicles)} vehicles.")
    
    # Refresh to get IDs
    for vehicle in vehicles:
        db.refresh(vehicle)
    
    return vehicles


def seed_availability_data(db: Session) -> None:
    """Generate random availability data for all vehicles for the next 3 months"""
    
    # Check if availability data already exists
    existing_count = db.query(VehicleAvailability).count()
    if existing_count > 0:
        print(f"Availability data already exists ({existing_count} records found). Skipping availability seeding.")
        return
    
    # Get all vehicles
    vehicles = db.query(Vehicle).all()
    if not vehicles:
        print("No vehicles found. Please seed vehicles first.")
        return
    
    # Generate availability for next 3 months
    start_date = date.today()
    end_date = start_date + timedelta(days=90)  # 3 months
    
    availability_records = []
    
    for vehicle in vehicles:
        current_date = start_date
        
        while current_date <= end_date:
            # Create availability periods of random length (1-7 days)
            period_length = random.randint(1, 7)
            period_end = min(current_date + timedelta(days=period_length - 1), end_date)
            
            # 80% chance of being available, 20% chance of being unavailable
            is_available = random.random() > 0.2
            
            availability_record = VehicleAvailability(
                vehicle_id=vehicle.id,
                start_date=current_date,
                end_date=period_end,
                is_available=is_available
            )
            
            availability_records.append(availability_record)
            db.add(availability_record)
            
            # Move to next period
            current_date = period_end + timedelta(days=1)
    
    db.commit()
    print(f"Successfully seeded {len(availability_records)} availability records for {len(vehicles)} vehicles.")


def initialize_database() -> None:
    """Initialize the database with tables and seed data"""
    print("Initializing database...")
    
    # Create all tables
    create_tables()
    print("Database tables created successfully.")
    
    # Create a database session
    db = SessionLocal()
    
    try:
        # Seed vehicles
        print("Seeding vehicles...")
        seed_vehicles(db)
        
        # Seed availability data
        print("Seeding availability data...")
        seed_availability_data(db)
        
        print("Database initialization completed successfully!")
        
    except Exception as e:
        print(f"Error during database initialization: {e}")
        db.rollback()
        raise
    finally:
        db.close()


def reset_database() -> None:
    """Reset the database by dropping and recreating all tables with fresh seed data"""
    print("Resetting database...")
    
    from models.database import drop_tables
    
    # Drop all tables
    drop_tables()
    print("All tables dropped.")
    
    # Reinitialize
    initialize_database()


if __name__ == "__main__":
    # Run database initialization
    initialize_database()