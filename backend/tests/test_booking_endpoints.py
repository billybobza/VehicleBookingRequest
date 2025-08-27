import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import date, datetime, timedelta
import json

from main import app
from models.database import Base, get_db, Vehicle, Booking, VehicleAvailability
from services.booking_service import BookingService

# Create test database
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_bookings.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    """Override database dependency for testing"""
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(scope="function")
def db_session():
    """Create a fresh database session for each test"""
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    yield db
    db.close()
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client():
    """Create a test client"""
    return TestClient(app)


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
def sample_booking_data():
    """Sample booking data for testing"""
    tomorrow = datetime.now() + timedelta(days=1)
    day_after = tomorrow + timedelta(days=1)
    
    return {
        "vehicle_id": 1,
        "start_datetime": tomorrow.isoformat(),
        "end_datetime": day_after.isoformat(),
        "reason": "Business meeting",
        "estimated_mileage": 150
    }


class TestBookingEndpoints:
    """Test cases for booking endpoints"""
    
    def test_create_booking_success(self, client, db_session, sample_vehicles, sample_booking_data):
        """Test successful booking creation"""
        response = client.post("/api/bookings/", json=sample_booking_data)
        assert response.status_code == 201
        
        data = response.json()
        assert data["vehicle_id"] == 1
        assert data["reason"] == "Business meeting"
        assert data["estimated_mileage"] == 150
        assert data["status"] == "confirmed"
        assert "id" in data
        assert "return_datetime" in data
        assert "created_at" in data
        assert data["vehicle"] is not None
        assert data["vehicle"]["registration"] == "ABC123"
    
    def test_create_booking_invalid_vehicle(self, client, db_session, sample_vehicles, sample_booking_data):
        """Test booking creation with invalid vehicle ID"""
        sample_booking_data["vehicle_id"] = 999  # Non-existent vehicle
        
        response = client.post("/api/bookings/", json=sample_booking_data)
        assert response.status_code == 404
        response_data = response.json()
        assert "not found" in response_data["message"]
    
    def test_create_booking_past_date(self, client, db_session, sample_vehicles):
        """Test booking creation with past start date"""
        yesterday = datetime.now() - timedelta(days=1)
        today = datetime.now()
        
        booking_data = {
            "vehicle_id": 1,
            "start_datetime": yesterday.isoformat(),
            "end_datetime": today.isoformat(),
            "reason": "Test booking",
            "estimated_mileage": 100
        }
        
        response = client.post("/api/bookings/", json=booking_data)
        assert response.status_code == 422  # Validation error
    
    def test_create_booking_end_before_start(self, client, db_session, sample_vehicles):
        """Test booking creation with end date before start date"""
        tomorrow = datetime.now() + timedelta(days=1)
        today = datetime.now()
        
        booking_data = {
            "vehicle_id": 1,
            "start_datetime": tomorrow.isoformat(),
            "end_datetime": today.isoformat(),  # End before start
            "reason": "Test booking",
            "estimated_mileage": 100
        }
        
        response = client.post("/api/bookings/", json=booking_data)
        assert response.status_code == 422  # Validation error
    
    def test_create_booking_missing_fields(self, client, db_session, sample_vehicles):
        """Test booking creation with missing required fields"""
        incomplete_data = {
            "vehicle_id": 1,
            "start_datetime": (datetime.now() + timedelta(days=1)).isoformat(),
            # Missing end_datetime, reason, estimated_mileage
        }
        
        response = client.post("/api/bookings/", json=incomplete_data)
        assert response.status_code == 422  # Validation error
    
    def test_create_booking_invalid_mileage(self, client, db_session, sample_vehicles, sample_booking_data):
        """Test booking creation with invalid estimated mileage"""
        sample_booking_data["estimated_mileage"] = -50  # Negative mileage
        
        response = client.post("/api/bookings/", json=sample_booking_data)
        assert response.status_code == 422  # Validation error
    
    def test_create_booking_vehicle_unavailable(self, client, db_session, sample_vehicles):
        """Test booking creation when vehicle is already booked"""
        # Create first booking
        tomorrow = datetime.now() + timedelta(days=1)
        day_after = tomorrow + timedelta(days=1)
        
        first_booking = Booking(
            vehicle_id=1,
            start_datetime=tomorrow,
            end_datetime=day_after,
            return_datetime=day_after,
            reason="Existing booking",
            estimated_mileage=100,
            status="confirmed"
        )
        db_session.add(first_booking)
        db_session.commit()
        
        # Try to create overlapping booking
        booking_data = {
            "vehicle_id": 1,
            "start_datetime": tomorrow.isoformat(),
            "end_datetime": day_after.isoformat(),
            "reason": "Conflicting booking",
            "estimated_mileage": 150
        }
        
        response = client.post("/api/bookings/", json=booking_data)
        assert response.status_code == 400
        response_data = response.json()
        assert "not available" in response_data["message"]
    
    def test_get_booking_success(self, client, db_session, sample_vehicles):
        """Test successful booking retrieval"""
        # Create a booking first
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
        
        response = client.get("/api/bookings/1")
        assert response.status_code == 200
        
        data = response.json()
        assert data["id"] == 1
        assert data["vehicle_id"] == 1
        assert data["reason"] == "Test booking"
        assert data["estimated_mileage"] == 100
        assert data["status"] == "confirmed"
        assert data["vehicle"] is not None
        assert data["vehicle"]["registration"] == "ABC123"
    
    def test_get_booking_not_found(self, client, db_session, sample_vehicles):
        """Test booking retrieval with non-existent ID"""
        response = client.get("/api/bookings/999")
        assert response.status_code == 404
        response_data = response.json()
        assert "not found" in response_data["message"]


class TestBookingService:
    """Test cases for BookingService business logic"""
    
    def test_calculate_return_date_weekday(self):
        """Test return date calculation for weekday"""
        # Tuesday end date should return at same time
        tuesday = datetime(2024, 1, 2, 15, 30)  # Tuesday 3:30 PM
        result = BookingService.calculate_return_date(tuesday)
        assert result == tuesday
    
    def test_calculate_return_date_friday(self):
        """Test return date calculation for Friday"""
        # Friday end date should return Monday 9:00 AM
        friday = datetime(2024, 1, 5, 15, 30)  # Friday 3:30 PM
        result = BookingService.calculate_return_date(friday)
        expected = datetime(2024, 1, 8, 9, 0)  # Monday 9:00 AM
        assert result == expected
    
    def test_calculate_return_date_saturday(self):
        """Test return date calculation for Saturday"""
        # Saturday end date should return Monday 9:00 AM
        saturday = datetime(2024, 1, 6, 15, 30)  # Saturday 3:30 PM
        result = BookingService.calculate_return_date(saturday)
        expected = datetime(2024, 1, 8, 9, 0)  # Monday 9:00 AM
        assert result == expected
    
    def test_calculate_return_date_sunday(self):
        """Test return date calculation for Sunday"""
        # Sunday end date should return Monday 9:00 AM
        sunday = datetime(2024, 1, 7, 15, 30)  # Sunday 3:30 PM
        result = BookingService.calculate_return_date(sunday)
        expected = datetime(2024, 1, 8, 9, 0)  # Monday 9:00 AM
        assert result == expected
    
    def test_calculate_return_date_monday(self):
        """Test return date calculation for Monday"""
        # Monday end date should return at same time
        monday = datetime(2024, 1, 1, 15, 30)  # Monday 3:30 PM
        result = BookingService.calculate_return_date(monday)
        assert result == monday
    
    def test_create_booking_success(self, db_session, sample_vehicles):
        """Test successful booking creation through service"""
        from schemas.booking import BookingCreate
        
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
        assert booking.reason == "Test booking"
        assert booking.estimated_mileage == 100
        assert booking.status == "confirmed"
        assert booking.return_datetime is not None
    
    def test_create_booking_invalid_vehicle(self, db_session, sample_vehicles):
        """Test booking creation with invalid vehicle ID through service"""
        from schemas.booking import BookingCreate
        
        tomorrow = datetime.now() + timedelta(days=1)
        day_after = tomorrow + timedelta(days=1)
        
        booking_data = BookingCreate(
            vehicle_id=999,  # Non-existent vehicle
            start_datetime=tomorrow,
            end_datetime=day_after,
            reason="Test booking",
            estimated_mileage=100
        )
        
        with pytest.raises(ValueError, match="not found"):
            BookingService.create_booking(db_session, booking_data)
    
    def test_create_booking_vehicle_unavailable(self, db_session, sample_vehicles):
        """Test booking creation when vehicle is unavailable through service"""
        from schemas.booking import BookingCreate
        
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
        
        with pytest.raises(ValueError, match="not available"):
            BookingService.create_booking(db_session, booking_data)
    
    def test_get_booking_by_id_success(self, db_session, sample_vehicles):
        """Test successful booking retrieval by ID through service"""
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
    
    def test_get_booking_by_id_not_found(self, db_session, sample_vehicles):
        """Test booking retrieval with non-existent ID through service"""
        booking = BookingService.get_booking_by_id(db_session, 999)
        assert booking is None
    
    def test_is_vehicle_available_for_booking_no_conflicts(self, db_session, sample_vehicles):
        """Test vehicle availability check with no conflicts"""
        tomorrow = datetime.now() + timedelta(days=1)
        day_after = tomorrow + timedelta(days=1)
        
        is_available = BookingService._is_vehicle_available_for_booking(
            db_session, 1, tomorrow, day_after
        )
        assert is_available is True
    
    def test_is_vehicle_available_for_booking_with_conflict(self, db_session, sample_vehicles):
        """Test vehicle availability check with booking conflict"""
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
        
        # Check availability for overlapping period
        is_available = BookingService._is_vehicle_available_for_booking(
            db_session, 1, tomorrow, day_after
        )
        assert is_available is False