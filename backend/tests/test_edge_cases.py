import pytest
from datetime import datetime, date, timedelta
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from models.database import Base, Vehicle, Booking, VehicleAvailability
from services.booking_service import BookingService
from services.vehicle_service import VehicleService
from schemas.booking import BookingCreate

# Create test database
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_edge_cases.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db_session():
    """Create a fresh database session for each test"""
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    yield db
    db.close()
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def sample_vehicles(db_session):
    """Create sample vehicles for testing"""
    vehicles = [
        Vehicle(id=1, registration="ABC123", make="Toyota", color="Red"),
        Vehicle(id=2, registration="DEF456", make="Honda", color="Blue"),
        Vehicle(id=3, registration="GHI789", make="Ford", color="Green")
    ]
    
    for vehicle in vehicles:
        db_session.add(vehicle)
    db_session.commit()
    
    return vehicles


class TestEdgeCasesAndBoundaryConditions:
    """Test edge cases and boundary conditions"""
    
    def test_booking_exactly_at_midnight(self, db_session, sample_vehicles):
        """Test booking that starts exactly at midnight"""
        midnight = datetime(2024, 1, 15, 0, 0, 0)
        next_midnight = datetime(2024, 1, 16, 0, 0, 0)
        
        booking_data = BookingCreate(
            vehicle_id=1,
            start_datetime=midnight,
            end_datetime=next_midnight,
            reason="Midnight booking",
            estimated_mileage=100
        )
        
        booking = BookingService.create_booking(db_session, booking_data)
        assert booking.start_datetime == midnight
        assert booking.end_datetime == next_midnight
    
    def test_booking_microsecond_precision(self, db_session, sample_vehicles):
        """Test booking with microsecond precision"""
        start = datetime(2024, 1, 15, 9, 30, 45, 123456)
        end = datetime(2024, 1, 15, 17, 30, 45, 654321)
        
        booking_data = BookingCreate(
            vehicle_id=1,
            start_datetime=start,
            end_datetime=end,
            reason="Microsecond precision test",
            estimated_mileage=50
        )
        
        booking = BookingService.create_booking(db_session, booking_data)
        assert booking.start_datetime == start
        assert booking.end_datetime == end
    
    def test_booking_very_short_duration(self, db_session, sample_vehicles):
        """Test booking with very short duration (1 minute)"""
        start = datetime(2024, 1, 15, 9, 0, 0)
        end = datetime(2024, 1, 15, 9, 1, 0)  # 1 minute
        
        booking_data = BookingCreate(
            vehicle_id=1,
            start_datetime=start,
            end_datetime=end,
            reason="Very short booking",
            estimated_mileage=1
        )
        
        booking = BookingService.create_booking(db_session, booking_data)
        assert booking.start_datetime == start
        assert booking.end_datetime == end
    
    def test_booking_very_long_duration(self, db_session, sample_vehicles):
        """Test booking with very long duration (1 year)"""
        start = datetime(2024, 1, 15, 9, 0, 0)
        end = datetime(2025, 1, 15, 9, 0, 0)  # 1 year
        
        booking_data = BookingCreate(
            vehicle_id=1,
            start_datetime=start,
            end_datetime=end,
            reason="Very long booking",
            estimated_mileage=50000
        )
        
        booking = BookingService.create_booking(db_session, booking_data)
        assert booking.start_datetime == start
        assert booking.end_datetime == end
    
    def test_return_date_calculation_leap_year(self, db_session, sample_vehicles):
        """Test return date calculation during leap year"""
        # February 29, 2024 (leap year) - Friday
        leap_friday = datetime(2024, 2, 29, 17, 0, 0)
        
        return_date = BookingService.calculate_return_date(leap_friday)
        expected = datetime(2024, 3, 4, 9, 0, 0)  # Monday March 4
        assert return_date == expected
    
    def test_return_date_calculation_year_boundary(self, db_session, sample_vehicles):
        """Test return date calculation across year boundary"""
        # December 31, 2023 (Sunday)
        year_end_sunday = datetime(2023, 12, 31, 15, 0, 0)
        
        return_date = BookingService.calculate_return_date(year_end_sunday)
        expected = datetime(2024, 1, 1, 9, 0, 0)  # Monday January 1, 2024
        assert return_date == expected
    
    def test_availability_check_same_second(self, db_session, sample_vehicles):
        """Test availability check for bookings that end/start at exact same second"""
        # Create existing booking
        start1 = datetime(2024, 1, 15, 9, 0, 0)
        end1 = datetime(2024, 1, 15, 17, 0, 0)
        
        existing_booking = Booking(
            vehicle_id=1,
            start_datetime=start1,
            end_datetime=end1,
            return_datetime=end1,
            reason="First booking",
            estimated_mileage=100,
            status="confirmed"
        )
        db_session.add(existing_booking)
        db_session.commit()
        
        # Try to book starting exactly when first booking ends
        start2 = datetime(2024, 1, 15, 17, 0, 0)  # Same second as end1
        end2 = datetime(2024, 1, 15, 19, 0, 0)
        
        is_available = BookingService._is_vehicle_available_for_booking(
            db_session, 1, start2, end2
        )
        # Should be available since end time is exclusive
        assert is_available is True
    
    def test_availability_check_one_second_overlap(self, db_session, sample_vehicles):
        """Test availability check with one second overlap"""
        # Create existing booking
        start1 = datetime(2024, 1, 15, 9, 0, 0)
        end1 = datetime(2024, 1, 15, 17, 0, 0)
        
        existing_booking = Booking(
            vehicle_id=1,
            start_datetime=start1,
            end_datetime=end1,
            return_datetime=end1,
            reason="First booking",
            estimated_mileage=100,
            status="confirmed"
        )
        db_session.add(existing_booking)
        db_session.commit()
        
        # Try to book starting one second before first booking ends
        start2 = datetime(2024, 1, 15, 16, 59, 59)  # 1 second before end1
        end2 = datetime(2024, 1, 15, 19, 0, 0)
        
        is_available = BookingService._is_vehicle_available_for_booking(
            db_session, 1, start2, end2
        )
        # Should not be available due to overlap
        assert is_available is False
    
    def test_maximum_estimated_mileage(self, db_session, sample_vehicles):
        """Test booking with maximum reasonable estimated mileage"""
        start = datetime(2024, 1, 15, 9, 0, 0)
        end = datetime(2024, 1, 16, 9, 0, 0)
        
        booking_data = BookingCreate(
            vehicle_id=1,
            start_datetime=start,
            end_datetime=end,
            reason="Long distance trip",
            estimated_mileage=999999  # Very high mileage
        )
        
        booking = BookingService.create_booking(db_session, booking_data)
        assert booking.estimated_mileage == 999999
    
    def test_minimum_estimated_mileage(self, db_session, sample_vehicles):
        """Test booking with minimum estimated mileage"""
        start = datetime(2024, 1, 15, 9, 0, 0)
        end = datetime(2024, 1, 15, 9, 5, 0)  # 5 minutes
        
        booking_data = BookingCreate(
            vehicle_id=1,
            start_datetime=start,
            end_datetime=end,
            reason="Very short trip",
            estimated_mileage=1  # Minimum mileage
        )
        
        booking = BookingService.create_booking(db_session, booking_data)
        assert booking.estimated_mileage == 1
    
    def test_very_long_reason_text(self, db_session, sample_vehicles):
        """Test booking with very long reason text"""
        start = datetime(2024, 1, 15, 9, 0, 0)
        end = datetime(2024, 1, 15, 17, 0, 0)
        
        long_reason = "A" * 5000  # Very long reason
        
        booking_data = BookingCreate(
            vehicle_id=1,
            start_datetime=start,
            end_datetime=end,
            reason=long_reason,
            estimated_mileage=100
        )
        
        booking = BookingService.create_booking(db_session, booking_data)
        assert booking.reason == long_reason
    
    def test_unicode_characters_in_reason(self, db_session, sample_vehicles):
        """Test booking with unicode characters in reason"""
        start = datetime(2024, 1, 15, 9, 0, 0)
        end = datetime(2024, 1, 15, 17, 0, 0)
        
        unicode_reason = "Meeting with 客户 about 项目 🚗 📅"
        
        booking_data = BookingCreate(
            vehicle_id=1,
            start_datetime=start,
            end_datetime=end,
            reason=unicode_reason,
            estimated_mileage=100
        )
        
        booking = BookingService.create_booking(db_session, booking_data)
        assert booking.reason == unicode_reason
    
    def test_availability_with_multiple_overlapping_records(self, db_session, sample_vehicles):
        """Test availability with multiple overlapping availability records"""
        today = date.today()
        
        # Create multiple overlapping availability records
        availability_records = [
            VehicleAvailability(
                vehicle_id=1,
                start_date=today,
                end_date=today + timedelta(days=10),
                is_available=True
            ),
            VehicleAvailability(
                vehicle_id=1,
                start_date=today + timedelta(days=5),
                end_date=today + timedelta(days=15),
                is_available=True
            ),
            VehicleAvailability(
                vehicle_id=1,
                start_date=today + timedelta(days=8),
                end_date=today + timedelta(days=12),
                is_available=False  # Conflicting record
            )
        ]
        
        for record in availability_records:
            db_session.add(record)
        db_session.commit()
        
        # Check availability in the conflicting period
        start_date = today + timedelta(days=9)
        end_date = today + timedelta(days=11)
        
        is_available = VehicleService._is_vehicle_available(db_session, 1, start_date, end_date)
        # Should not be available due to the unavailable record
        assert is_available is False
    
    def test_booking_status_edge_cases(self, db_session, sample_vehicles):
        """Test booking with different status values"""
        start = datetime(2024, 1, 15, 9, 0, 0)
        end = datetime(2024, 1, 15, 17, 0, 0)
        
        # Create bookings with different statuses
        statuses = ["confirmed", "pending", "cancelled", "completed"]
        
        for i, status in enumerate(statuses):
            booking = Booking(
                vehicle_id=1,
                start_datetime=start + timedelta(days=i),
                end_datetime=end + timedelta(days=i),
                return_datetime=end + timedelta(days=i),
                reason=f"Booking with {status} status",
                estimated_mileage=100,
                status=status
            )
            db_session.add(booking)
        
        db_session.commit()
        
        # Only confirmed bookings should affect availability
        future_start = start + timedelta(days=10)
        future_end = end + timedelta(days=10)
        
        is_available = BookingService._is_vehicle_available_for_booking(
            db_session, 1, future_start, future_end
        )
        assert is_available is True
    
    def test_vehicle_registration_edge_cases(self, db_session):
        """Test vehicles with edge case registration formats"""
        edge_case_vehicles = [
            Vehicle(id=10, registration="A1", make="Mini", color="Red"),  # Very short
            Vehicle(id=11, registration="VERYLONGREGISTRATION123", make="Custom", color="Blue"),  # Very long
            Vehicle(id=12, registration="123-ABC-456", make="Truck", color="Green"),  # With dashes
            Vehicle(id=13, registration="ABC 123", make="Van", color="White"),  # With space
            Vehicle(id=14, registration="αβγ123", make="International", color="Black"),  # Unicode
        ]
        
        for vehicle in edge_case_vehicles:
            db_session.add(vehicle)
        db_session.commit()
        
        # Verify all vehicles were created successfully
        all_vehicles = VehicleService.get_all_vehicles(db_session)
        registrations = [v.registration for v in all_vehicles]
        
        assert "A1" in registrations
        assert "VERYLONGREGISTRATION123" in registrations
        assert "123-ABC-456" in registrations
        assert "ABC 123" in registrations
        assert "αβγ123" in registrations
    
    def test_date_boundary_conditions(self, db_session, sample_vehicles):
        """Test date boundary conditions for availability"""
        today = date.today()
        
        # Create availability record
        availability = VehicleAvailability(
            vehicle_id=1,
            start_date=today + timedelta(days=5),
            end_date=today + timedelta(days=10),
            is_available=True
        )
        db_session.add(availability)
        db_session.commit()
        
        # Test exact boundary dates
        is_available_start = VehicleService._is_vehicle_available(
            db_session, 1, today + timedelta(days=5), today + timedelta(days=5)
        )
        assert is_available_start is True
        
        is_available_end = VehicleService._is_vehicle_available(
            db_session, 1, today + timedelta(days=10), today + timedelta(days=10)
        )
        assert is_available_end is True
        
        # Test just outside boundaries
        is_available_before = VehicleService._is_vehicle_available(
            db_session, 1, today + timedelta(days=4), today + timedelta(days=4)
        )
        assert is_available_before is True  # No conflicting records
        
        is_available_after = VehicleService._is_vehicle_available(
            db_session, 1, today + timedelta(days=11), today + timedelta(days=11)
        )
        assert is_available_after is True  # No conflicting records
    
    def test_concurrent_booking_simulation(self, db_session, sample_vehicles):
        """Simulate concurrent booking attempts"""
        start = datetime(2024, 1, 15, 9, 0, 0)
        end = datetime(2024, 1, 15, 17, 0, 0)
        
        booking_data = BookingCreate(
            vehicle_id=1,
            start_datetime=start,
            end_datetime=end,
            reason="Concurrent booking test",
            estimated_mileage=100
        )
        
        # First booking should succeed
        booking1 = BookingService.create_booking(db_session, booking_data)
        assert booking1.id is not None
        
        # Second booking for same time should fail
        with pytest.raises(ValueError, match="not available"):
            BookingService.create_booking(db_session, booking_data)
    
    def test_database_constraint_violations(self, db_session):
        """Test database constraint violations"""
        # Try to create vehicle with duplicate registration
        vehicle1 = Vehicle(id=1, registration="DUPLICATE", make="Toyota", color="Red")
        vehicle2 = Vehicle(id=2, registration="DUPLICATE", make="Honda", color="Blue")
        
        db_session.add(vehicle1)
        db_session.commit()
        
        db_session.add(vehicle2)
        
        # Should raise integrity error due to unique constraint
        with pytest.raises(Exception):  # SQLAlchemy will raise IntegrityError
            db_session.commit()
    
    def test_large_dataset_performance(self, db_session):
        """Test performance with large dataset"""
        # Create many vehicles
        vehicles = []
        for i in range(100):
            vehicle = Vehicle(
                id=i + 1,
                registration=f"REG{i:03d}",
                make=f"Make{i % 10}",
                color=f"Color{i % 5}"
            )
            vehicles.append(vehicle)
        
        db_session.add_all(vehicles)
        db_session.commit()
        
        # Create many bookings
        start_base = datetime(2024, 1, 15, 9, 0, 0)
        bookings = []
        for i in range(50):
            booking = Booking(
                vehicle_id=(i % 100) + 1,
                start_datetime=start_base + timedelta(days=i),
                end_datetime=start_base + timedelta(days=i, hours=8),
                return_datetime=start_base + timedelta(days=i, hours=8),
                reason=f"Booking {i}",
                estimated_mileage=100 + i,
                status="confirmed"
            )
            bookings.append(booking)
        
        db_session.add_all(bookings)
        db_session.commit()
        
        # Test performance of getting all vehicles
        all_vehicles = VehicleService.get_all_vehicles(db_session)
        assert len(all_vehicles) == 100
        
        # Test performance of availability check
        future_date = date.today() + timedelta(days=200)
        available_vehicles = VehicleService.get_available_vehicles(
            db_session, future_date, future_date + timedelta(days=1)
        )
        # Should return all vehicles since no conflicts in future
        assert len(available_vehicles) == 100