#!/usr/bin/env python3
"""
Database management CLI for the car booking system
"""

import argparse
import sys
from datetime import date, timedelta
from sqlalchemy.orm import Session

from database_init import initialize_database, reset_database, seed_vehicles, seed_availability_data
from migrations.migration_manager import get_migration_manager
from models.database import SessionLocal, Vehicle, Booking, VehicleAvailability
from db_utils import get_all_vehicles, get_available_vehicles


def show_status():
    """Show database status and statistics"""
    print("=== Car Booking System Database Status ===\n")
    
    try:
        with SessionLocal() as db:
            # Migration status
            migration_manager = get_migration_manager()
            status = migration_manager.get_migration_status(db)
            
            print("Migration Information:")
            print(f"  Current Version: {status['current_version']}")
            print(f"  Applied Migrations: {status['migration_count']}")
            print(f"  Last Migration: {status['last_migration_date']}")
            print()
            
            # Data statistics
            vehicle_count = db.query(Vehicle).count()
            booking_count = db.query(Booking).count()
            availability_count = db.query(VehicleAvailability).count()
            
            print("Data Statistics:")
            print(f"  Vehicles: {vehicle_count}")
            print(f"  Bookings: {booking_count}")
            print(f"  Availability Records: {availability_count}")
            print()
            
            # Recent bookings
            recent_bookings = db.query(Booking).order_by(Booking.created_at.desc()).limit(5).all()
            if recent_bookings:
                print("Recent Bookings:")
                for booking in recent_bookings:
                    print(f"  ID {booking.id}: Vehicle {booking.vehicle_id} - {booking.start_datetime.strftime('%Y-%m-%d %H:%M')} to {booking.end_datetime.strftime('%Y-%m-%d %H:%M')}")
            else:
                print("Recent Bookings: None")
            print()
            
            # Available vehicles for today
            today = date.today()
            tomorrow = today + timedelta(days=1)
            available_today = get_available_vehicles(db, today, tomorrow)
            
            print(f"Vehicles Available Today ({today}):")
            if available_today:
                for vehicle in available_today:
                    print(f"  {vehicle.registration} - {vehicle.make} ({vehicle.color})")
            else:
                print("  No vehicles available")
                
    except Exception as e:
        print(f"Error retrieving database status: {e}")
        sys.exit(1)


def list_vehicles():
    """List all vehicles in the database"""
    print("=== All Vehicles ===\n")
    
    try:
        with SessionLocal() as db:
            vehicles = get_all_vehicles(db)
            
            if not vehicles:
                print("No vehicles found in database.")
                return
            
            print(f"Found {len(vehicles)} vehicles:\n")
            print("ID | Registration | Make        | Color   | Created")
            print("-" * 55)
            
            for vehicle in vehicles:
                created = vehicle.created_at.strftime('%Y-%m-%d') if vehicle.created_at else 'Unknown'
                print(f"{vehicle.id:2d} | {vehicle.registration:12s} | {vehicle.make:11s} | {vehicle.color:7s} | {created}")
                
    except Exception as e:
        print(f"Error listing vehicles: {e}")
        sys.exit(1)


def check_availability(start_date_str: str, end_date_str: str):
    """Check vehicle availability for a date range"""
    try:
        start_date = date.fromisoformat(start_date_str)
        end_date = date.fromisoformat(end_date_str)
    except ValueError:
        print("Error: Invalid date format. Use YYYY-MM-DD format.")
        sys.exit(1)
    
    if start_date > end_date:
        print("Error: Start date must be before end date.")
        sys.exit(1)
    
    print(f"=== Vehicle Availability: {start_date} to {end_date} ===\n")
    
    try:
        with SessionLocal() as db:
            available_vehicles = get_available_vehicles(db, start_date, end_date)
            all_vehicles = get_all_vehicles(db)
            
            print(f"Available vehicles: {len(available_vehicles)} of {len(all_vehicles)}\n")
            
            if available_vehicles:
                print("Available Vehicles:")
                print("Registration | Make        | Color")
                print("-" * 35)
                for vehicle in available_vehicles:
                    print(f"{vehicle.registration:12s} | {vehicle.make:11s} | {vehicle.color}")
            else:
                print("No vehicles available for the specified period.")
            
            # Show unavailable vehicles
            unavailable = [v for v in all_vehicles if v not in available_vehicles]
            if unavailable:
                print(f"\nUnavailable Vehicles ({len(unavailable)}):")
                print("Registration | Make        | Color")
                print("-" * 35)
                for vehicle in unavailable:
                    print(f"{vehicle.registration:12s} | {vehicle.make:11s} | {vehicle.color}")
                
    except Exception as e:
        print(f"Error checking availability: {e}")
        sys.exit(1)


def seed_data():
    """Seed the database with initial data"""
    print("=== Seeding Database ===\n")
    
    try:
        with SessionLocal() as db:
            print("Seeding vehicles...")
            seed_vehicles(db)
            
            print("Seeding availability data...")
            seed_availability_data(db)
            
            print("Database seeding completed successfully!")
            
    except Exception as e:
        print(f"Error seeding database: {e}")
        sys.exit(1)


def main():
    """Main CLI function"""
    parser = argparse.ArgumentParser(
        description="Car Booking System Database Management CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python manage_db.py status                    # Show database status
  python manage_db.py init                      # Initialize database
  python manage_db.py reset                     # Reset database (WARNING: deletes all data)
  python manage_db.py vehicles                  # List all vehicles
  python manage_db.py availability 2024-01-15 2024-01-17  # Check availability
  python manage_db.py seed                      # Seed database with initial data
        """
    )
    
    parser.add_argument(
        'command',
        choices=['status', 'init', 'reset', 'vehicles', 'availability', 'seed'],
        help='Database management command'
    )
    
    parser.add_argument(
        'start_date',
        nargs='?',
        help='Start date for availability check (YYYY-MM-DD)'
    )
    
    parser.add_argument(
        'end_date',
        nargs='?',
        help='End date for availability check (YYYY-MM-DD)'
    )
    
    args = parser.parse_args()
    
    if args.command == 'status':
        show_status()
    elif args.command == 'init':
        print("Initializing database...")
        initialize_database()
        print("Database initialization completed!")
    elif args.command == 'reset':
        response = input("WARNING: This will delete all data. Are you sure? (yes/no): ")
        if response.lower() == 'yes':
            print("Resetting database...")
            reset_database()
            print("Database reset completed!")
        else:
            print("Database reset cancelled.")
    elif args.command == 'vehicles':
        list_vehicles()
    elif args.command == 'availability':
        if not args.start_date or not args.end_date:
            print("Error: availability command requires start_date and end_date arguments")
            parser.print_help()
            sys.exit(1)
        check_availability(args.start_date, args.end_date)
    elif args.command == 'seed':
        seed_data()


if __name__ == "__main__":
    main()