import pytest
from datetime import datetime, date, timedelta
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from models.database import Base, Vehicle, Booking, VehicleAvailability
from services.booking_service import BookingService
from services.vehicle_service import VehicleService
from schemas.booking import BookingCreate

# Create test database
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_business_logic.db"
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


@pytest.fixture
def sample_availability(db_session, sample_vehicles):
    """Create sample availability records"""
    today = date.today()
    availability_records = [
        # Vehicle 1 available for next 30 days
        VehicleAvailability(
            vehicle_id=1,
            start_date=today,
            end_date=today + timedelta(days=30),
            is_available=True
        ),
        # Vehicle 2 available for next 30 days
        VehicleAvailability(
            vehicle_id=2,
            start_date=today,
            end_date=today + timedelta(days=30),
            is_available=True
        ),
        # Vehicle 3 not available for next 10 days
        VehicleAvailability(
            vehicle_id=3,
            start_date=today,
            end_date=today + timedelta(days=10),
            is_available=False
        )
    ]
    
    for record in availability_records:
        db_session.add(record)
    db_session.commit()
    
    return availability_records


class TestBookingServiceBusinessLogic:
    """Comprehensive tests for BookingService business logic"""
    
    def test_calculate_return_date_monday(self):
        """Test return date calculation for Monday"""
        monday = datetime(2024, 1, 1, 15, 30)  # Monday 3:30 PM
        result = BookingService.calculate_return_date(monday)
        assert result == monday
    
    def test_calculate_return_date_tuesday(self):
        """Test return date calculation for Tuesday"""
        tuesday = datetime(2024, 1, 2, 15, 30)  # Tuesday 3:30 PM
        result = BookingService.calculate_return_date(tuesday)
        assert result == tuesday
    
    def test_calculate_return_date_wednesday(self):
        """Test return date calculation for Wednesday"""
        wednesday = datetime(2024, 1, 3, 15, 30)  # Wednesday 3:30 PM
        result = BookingService.calculate_return_date(wednesday)
        assert result == wednesday
    
    def test_calculate_return_date_thursday(self):
        """Test return date calculation for Thursday"""
        thursday = datetime(2024, 1, 4, 15, 30)  # Thursday 3:30 PM
        result = BookingService.calculate_return_date(thursday)
        assert result == thursday
    
    def test_calculate_return_date_friday(self):
        """Test return date calculation for Friday"""
        friday = datetime(2024, 1, 5, 15, 30)  # Friday 3:30 PM
        result = BookingService.calculate_return_date(friday)
        expected = datetime(2024, 1, 8, 9, 0)  # Monday 9:00 AM
        assert result == expected
    
    def test_calculate_return_date_saturday(self):
        """Test return date calculation for Saturday"""
        saturday = datetime(2024, 1, 6, 15, 30)  # Saturday 3:30 PM
        result = BookingService.calculate_return_date(saturday)
        expected = datetime(2024, 1, 8, 9, 0)  # Monday 9:00 AM
        assert result == expected
    
    def test_calculate_return_date_sunday(self):
        """Test return date calculation for Sunday"""
        sunday = datetime(2024, 1, 7, 15, 30)  # Sunday 3:30 PM
        result = BookingService.calculate_return_date(sunday)
        expected = datetime(2024, 1, 8, 9, 0)  # Monday 9:00 AM
        assert result == expected
    
    def test_calculate_return_date_edge_case_midnight(self):
        """Test return date calculation for Friday at midnight"""
        friday_midnight = datetime(2024, 1, 5, 0, 0)  # Friday midnight
        result = BookingService.calculate_return_date(friday_midnight)
        expected = datetime(2024, 1, 8, 9, 0)  # Monday 9:00 AM
        assert result == expected
    
    def test_calculate_return_date_edge_case_late_night(self):
        """Test return date calculation for Friday late night"""
        friday_late = datetime(2024, 1, 5, 23, 59)  # Friday 11:59 PM
        result = BookingService.calculate_return_date(friday_late)
        expected = datetime(2024, 1, 8, 9, 0)  # Monday 9:00 AM
        assert result == expected
    
    def test_is_vehicle_available_no_conflicts(self, db_session, sample_vehicles):
        """Test vehicle availability check with no conflicts"""
        tomorrow = datetime.now() + timedelta(days=1)
        day_after = tomorrow + timedelta(days=1)
        
        is_available = BookingService._is_vehicle_available_for_booking(
            db_session, 1, tomorrow, day_after
        )
        assert is_available is True
    
    def test_is_vehicle_available_exact_overlap(self, db_session, sample_vehicles):
        """Test vehicle availability check with exact time overlap"""
        # Create existing booking
        tomorrow = datetime.now() + timedelta(days=1)
        day_after = tomorrow + timedelta(days=1)
        
        existing_booking = Booking(
            vehicle_id=1,
            start_datetime=tomorrow,
            end_datetime=day_after,
            return_datetime=day_after,
            reason="Existing booking",
            estimated_mileage=100,
            status="confirmed"
        )
        db_session.add(existing_booking)
        db_session.commit()
        
        # Check availability for exact same period
        is_available = BookingService._is_vehicle_available_for_booking(
            db_session, 1, tomorrow, day_after
        )
        assert is_available is False
    
    def test_is_vehicle_available_partial_overlap_start(self, db_session, sample_vehicles):
        """Test vehicle availability check with partial overlap at start"""
        # Create existing booking
        tomorrow = datetime.now() + timedelta(days=1)
        day_after = tomorrow + timedelta(days=1)
        
        existing_booking = Booking(
            vehicle_id=1,
            start_datetime=tomorrow,
            end_datetime=day_after,
            return_datetime=day_after,
            reason="Existing booking",
            estimated_mileage=100,
            status="confirmed"
        )
        db_session.add(existing_booking)
        db_session.commit()
        
        # Check availability for period that starts during existing booking
        overlap_start = tomorrow + timedelta(hours=12)
        overlap_end = day_after + timedelta(hours=12)
        
        is_available = BookingService._is_vehicle_available_for_booking(
            db_session, 1, overlap_start, overlap_end
        )
        assert is_available is False
    
    def test_is_vehicle_available_partial_overlap_end(self, db_session, sample_vehicles):
        """Test vehicle availability check with partial overlap at end"""
        # Create existing booking
        tomorrow = datetime.now() + timedelta(days=1)
        day_after = tomorrow + timedelta(days=1)
        
        existing_booking = Booking(
            vehicle_id=1,
            start_datetime=tomorrow,
            end_datetime=day_after,
            return_datetime=day_after,
            reason="Existing booking",
            estimated_mileage=100,
            status="confirmed"
        )
        db_session.add(existing_booking)
        db_session.commit()
        
        # Check availability for period that ends during existing booking
        overlap_start = tomorrow - timedelta(hours=12)
        overlap_end = tomorrow + timedelta(hours=12)
        
        is_available = BookingService._is_vehicle_available_for_booking(
            db_session, 1, overlap_start, overlap_end
        )
        assert is_available is False
    
    def test_is_vehicle_available_encompassing_overlap(self, db_session, sample_vehicles):
        """Test vehicle availability check with encompassing overlap"""
        # Create existing booking
        tomorrow = datetime.now() + timedelta(days=1)
        day_after = tomorrow + timedelta(days=1)
        
        existing_booking = Booking(
            vehicle_id=1,
            start_datetime=tomorrow,
            end_datetime=day_after,
            return_datetime=day_after,
            reason="Existing booking",
            estimated_mileage=100,
            status="confirmed"
        )
        db_session.add(existing_booking)
        db_session.commit()
        
        # Check availability for period that encompasses existing booking
        encompass_start = tomorrow - timedelta(hours=12)
        encompass_end = day_after + timedelta(hours=12)
        
        is_available = BookingService._is_vehicle_available_for_booking(
            db_session, 1, encompass_start, encompass_end
        )
        assert is_available is False
    
    def test_is_vehicle_available_adjacent_bookings(self, db_session, sample_vehicles):
        """Test vehicle availability check with adjacent bookings (no overlap)"""
        # Create existing booking
        tomorrow = datetime.now() + timedelta(days=1)
        day_after = tomorrow + timedelta(days=1)
        
        existing_booking = Booking(
            vehicle_id=1,
            start_datetime=tomorrow,
            end_datetime=day_after,
            return_datetime=day_after,
            reason="Existing booking",
            estimated_mileage=100,
            status="confirmed"
        )
        db_session.add(existing_booking)
        db_session.commit()
        
        # Check availability for period immediately after existing booking
        adjacent_start = day_after
        adjacent_end = day_after + timedelta(days=1)
        
        is_available = BookingService._is_vehicle_available_for_booking(
            db_session, 1, adjacent_start, adjacent_end
        )
        assert is_available is True
    
    def test_is_vehicle_available_different_vehicle(self, db_session, sample_vehicles):
        """Test vehicle availability check for different vehicle"""
        # Create existing booking for vehicle 1
        tomorrow = datetime.now() + timedelta(days=1)
        day_after = tomorrow + timedelta(days=1)
        
        existing_booking = Booking(
            vehicle_id=1,
            start_datetime=tomorrow,
            end_datetime=day_after,
            return_datetime=day_after,
            reason="Existing booking",
            estimated_mileage=100,
            status="confirmed"
        )
        db_session.add(existing_booking)
        db_session.commit()
        
        # Check availability for vehicle 2 during same period
        is_available = BookingService._is_vehicle_available_for_booking(
            db_session, 2, tomorrow, day_after
        )
        assert is_available is True
    
    def test_is_vehicle_available_cancelled_booking(self, db_session, sample_vehicles):
        """Test vehicle availability check ignores cancelled bookings"""
        # Create cancelled booking
        tomorrow = datetime.now() + timedelta(days=1)
        day_after = tomorrow + timedelta(days=1)
        
        cancelled_booking = Booking(
            vehicle_id=1,
            start_datetime=tomorrow,
            end_datetime=day_after,
            return_datetime=day_after,
            reason="Cancelled booking",
            estimated_mileage=100,
            status="cancelled"
        )
        db_session.add(cancelled_booking)
        db_session.commit()
        
        # Check availability for same period
        is_available = BookingService._is_vehicle_available_for_booking(
            db_session, 1, tomorrow, day_after
        )
        assert is_available is True
    
    def test_create_booking_success(self, db_session, sample_vehicles):
        """Test successful booking creation"""
        tomorrow = datetime.now() + timedelta(days=1)
        day_after = tomorrow + timedelta(days=1)
        
        booking_data = BookingCreate(
            vehicle_id=1,
            start_datetime=tomorrow,
            end_datetime=day_after,
            reason="Test booking",
            estimated_mileage=100
        )
        
        booking = BookingService.create_booking(db_session, booking_data)
        
        assert booking.id is not None
        assert booking.vehicle_id == 1
        assert booking.start_datetime == tomorrow
        assert booking.end_datetime == day_after
        assert booking.reason == "Test booking"
        assert booking.estimated_mileage == 100
        assert booking.status == "confirmed"
        assert booking.return_datetime is not None
        assert booking.created_at is not None
    
    def test_create_booking_friday_return_calculation(self, db_session, sample_vehicles):
        """Test booking creation with Friday end date calculates correct return date"""
        # Use a future Friday
        base_date = datetime.now() + timedelta(days=30)
        # Find next Friday
        while base_date.weekday() != 4:  # 4 = Friday
            base_date += timedelta(days=1)
        
        friday = base_date.replace(hour=15, minute=30, second=0, microsecond=0)
        saturday = friday + timedelta(hours=2)
        
        booking_data = BookingCreate(
            vehicle_id=1,
            start_datetime=friday,
            end_datetime=saturday,
            reason="Friday booking",
            estimated_mileage=50
        )
        
        booking = BookingService.create_booking(db_session, booking_data)
        
        # Return date should be Monday 9:00 AM
        expected_return_date = friday.date() + timedelta(days=3)  # Friday + 3 = Monday
        expected_return = datetime.combine(expected_return_date, datetime.min.time().replace(hour=9))
        assert booking.return_datetime == expected_return
    
    def test_create_booking_nonexistent_vehicle(self, db_session, sample_vehicles):
        """Test booking creation with non-existent vehicle"""
        tomorrow = datetime.now() + timedelta(days=1)
        day_after = tomorrow + timedelta(days=1)
        
        booking_data = BookingCreate(
            vehicle_id=999,  # Non-existent vehicle
            start_datetime=tomorrow,
            end_datetime=day_after,
            reason="Test booking",
            estimated_mileage=100
        )
        
        with pytest.raises(ValueError, match="Vehicle with ID 999 not found"):
            BookingService.create_booking(db_session, booking_data)
    
    def test_create_booking_vehicle_unavailable(self, db_session, sample_vehicles):
        """Test booking creation when vehicle is unavailable"""
        # Create existing booking
        tomorrow = datetime.now() + timedelta(days=1)
        day_after = tomorrow + timedelta(days=1)
        
        existing_booking = Booking(
            vehicle_id=1,
            start_datetime=tomorrow,
            end_datetime=day_after,
            return_datetime=day_after,
            reason="Existing booking",
            estimated_mileage=100,
            status="confirmed"
        )
        db_session.add(existing_booking)
        db_session.commit()
        
        # Try to create overlapping booking
        booking_data = BookingCreate(
            vehicle_id=1,
            start_datetime=tomorrow,
            end_datetime=day_after,
            reason="Conflicting booking",
            estimated_mileage=150
        )
        
        with pytest.raises(ValueError, match="Vehicle is not available"):
            BookingService.create_booking(db_session, booking_data)
    
    def test_get_booking_by_id_success(self, db_session, sample_vehicles):
        """Test successful booking retrieval by ID"""
        # Create a booking
        tomorrow = datetime.now() + timedelta(days=1)
        day_after = tomorrow + timedelta(days=1)
        
        booking = Booking(
            id=1,
            vehicle_id=1,
            start_datetime=tomorrow,
            end_datetime=day_after,
            return_datetime=day_after,
            reason="Test booking",
            estimated_mileage=100,
            status="confirmed"
        )
        db_session.add(booking)
        db_session.commit()
        
        # Retrieve booking
        retrieved_booking = BookingService.get_booking_by_id(db_session, 1)
        
        assert retrieved_booking is not None
        assert retrieved_booking.id == 1
        assert retrieved_booking.reason == "Test booking"
        assert retrieved_booking.estimated_mileage == 100
    
    def test_get_booking_by_id_not_found(self, db_session, sample_vehicles):
        """Test booking retrieval with non-existent ID"""
        booking = BookingService.get_booking_by_id(db_session, 999)
        assert booking is None


class TestVehicleServiceBusinessLogic:
    """Comprehensive tests for VehicleService business logic"""
    
    def test_get_all_vehicles_empty(self, db_session):
        """Test getting all vehicles when database is empty"""
        vehicles = VehicleService.get_all_vehicles(db_session)
        assert len(vehicles) == 0
    
    def test_get_all_vehicles_with_data(self, db_session, sample_vehicles):
        """Test getting all vehicles with sample data"""
        vehicles = VehicleService.get_all_vehicles(db_session)
        assert len(vehicles) == 3
        assert vehicles[0].registration == "ABC123"
        assert vehicles[1].registration == "DEF456"
        assert vehicles[2].registration == "GHI789"
    
    def test_get_available_vehicles_no_restrictions(self, db_session, sample_vehicles, sample_availability):
        """Test getting available vehicles with no booking restrictions"""
        today = date.today()
        start_date = today + timedelta(days=5)
        end_date = today + timedelta(days=7)
        
        vehicles = VehicleService.get_available_vehicles(db_session, start_date, end_date)
        
        # Should return vehicles 1 and 2 (vehicle 3 is marked unavailable)
        assert len(vehicles) == 2
        registrations = [v.registration for v in vehicles]
        assert "ABC123" in registrations
        assert "DEF456" in registrations
        assert "GHI789" not in registrations
    
    def test_get_available_vehicles_with_booking_conflict(self, db_session, sample_vehicles, sample_availability):
        """Test getting available vehicles with booking conflicts"""
        today = date.today()
        start_date = today + timedelta(days=1)
        end_date = today + timedelta(days=2)
        
        # Create booking for vehicle 1
        booking = Booking(
            vehicle_id=1,
            start_datetime=datetime.combine(start_date, datetime.min.time()),
            end_datetime=datetime.combine(end_date, datetime.max.time()),
            return_datetime=datetime.combine(end_date, datetime.max.time()),
            reason="Existing booking",
            estimated_mileage=100,
            status="confirmed"
        )
        db_session.add(booking)
        db_session.commit()
        
        vehicles = VehicleService.get_available_vehicles(db_session, start_date, end_date)
        
        # Should only return vehicle 2
        assert len(vehicles) == 1
        assert vehicles[0].registration == "DEF456"
    
    def test_is_vehicle_available_no_conflicts(self, db_session, sample_vehicles, sample_availability):
        """Test vehicle availability check with no conflicts"""
        today = date.today()
        start_date = today + timedelta(days=5)
        end_date = today + timedelta(days=7)
        
        # Vehicle 1 should be available
        is_available = VehicleService._is_vehicle_available(db_session, 1, start_date, end_date)
        assert is_available is True
        
        # Vehicle 2 should be available
        is_available = VehicleService._is_vehicle_available(db_session, 2, start_date, end_date)
        assert is_available is True
        
        # Vehicle 3 should not be available (marked as unavailable in seed data)
        is_available = VehicleService._is_vehicle_available(db_session, 3, start_date, end_date)
        assert is_available is False
    
    def test_is_vehicle_available_with_booking_conflict(self, db_session, sample_vehicles, sample_availability):
        """Test vehicle availability check with booking conflicts"""
        today = date.today()
        start_date = today + timedelta(days=1)
        end_date = today + timedelta(days=2)
        
        # Create booking for vehicle 1
        booking = Booking(
            vehicle_id=1,
            start_datetime=datetime.combine(start_date, datetime.min.time()),
            end_datetime=datetime.combine(end_date, datetime.max.time()),
            return_datetime=datetime.combine(end_date, datetime.max.time()),
            reason="Existing booking",
            estimated_mileage=100,
            status="confirmed"
        )
        db_session.add(booking)
        db_session.commit()
        
        # Vehicle 1 should not be available due to booking
        is_available = VehicleService._is_vehicle_available(db_session, 1, start_date, end_date)
        assert is_available is False
        
        # Vehicle 2 should be available (no booking conflict)
        is_available = VehicleService._is_vehicle_available(db_session, 2, start_date, end_date)
        assert is_available is True
    
    def test_is_vehicle_available_edge_case_same_day(self, db_session, sample_vehicles, sample_availability):
        """Test vehicle availability for same day booking"""
        today = date.today()
        start_date = today + timedelta(days=5)
        end_date = today + timedelta(days=5)  # Same day
        
        is_available = VehicleService._is_vehicle_available(db_session, 1, start_date, end_date)
        assert is_available is True
    
    def test_is_vehicle_available_no_availability_records(self, db_session, sample_vehicles):
        """Test vehicle availability when no availability records exist"""
        today = date.today()
        start_date = today + timedelta(days=5)
        end_date = today + timedelta(days=7)
        
        # Should assume available when no records exist
        is_available = VehicleService._is_vehicle_available(db_session, 1, start_date, end_date)
        assert is_available is True
    
    def test_is_vehicle_available_partial_availability_coverage(self, db_session, sample_vehicles):
        """Test vehicle availability with partial availability record coverage"""
        today = date.today()
        
        # Create availability record that only partially covers requested period
        partial_availability = VehicleAvailability(
            vehicle_id=1,
            start_date=today + timedelta(days=1),
            end_date=today + timedelta(days=3),  # Only covers part of requested period
            is_available=True
        )
        db_session.add(partial_availability)
        db_session.commit()
        
        # Request period that extends beyond availability record
        start_date = today + timedelta(days=2)
        end_date = today + timedelta(days=5)
        
        # Should be available since no unavailable records conflict
        is_available = VehicleService._is_vehicle_available(db_session, 1, start_date, end_date)
        assert is_available is True
    
    def test_is_vehicle_available_multiple_availability_records(self, db_session, sample_vehicles):
        """Test vehicle availability with multiple overlapping availability records"""
        today = date.today()
        
        # Create multiple availability records
        availability1 = VehicleAvailability(
            vehicle_id=1,
            start_date=today,
            end_date=today + timedelta(days=10),
            is_available=True
        )
        availability2 = VehicleAvailability(
            vehicle_id=1,
            start_date=today + timedelta(days=5),
            end_date=today + timedelta(days=15),
            is_available=True
        )
        db_session.add(availability1)
        db_session.add(availability2)
        db_session.commit()
        
        start_date = today + timedelta(days=7)
        end_date = today + timedelta(days=9)
        
        is_available = VehicleService._is_vehicle_available(db_session, 1, start_date, end_date)
        assert is_available is True