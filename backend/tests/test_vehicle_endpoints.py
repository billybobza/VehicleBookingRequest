import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import date, datetime, timedelta
import json

from main import app
from models.database import Base, get_db, Vehicle, Booking, VehicleAvailability
from services.vehicle_service import VehicleService

# Create test database
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_vehicles.db"
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
def sample_bookings(db_session, sample_vehicles):
    """Create sample bookings for testing"""
    today = date.today()
    bookings = [
        Booking(
            id=1,
            vehicle_id=1,
            start_datetime=datetime.combine(today + timedelta(days=1), datetime.min.time()),
            end_datetime=datetime.combine(today + timedelta(days=2), datetime.max.time()),
            return_datetime=datetime.combine(today + timedelta(days=3), datetime.min.time()),
            reason="Business meeting",
            estimated_mileage=100,
            status="confirmed"
        )
    ]
    
    for booking in bookings:
        db_session.add(booking)
    db_session.commit()
    
    return bookings


@pytest.fixture
def sample_availability(db_session, sample_vehicles):
    """Create sample availability records for testing"""
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


class TestVehicleEndpoints:
    """Test cases for vehicle endpoints"""
    
    def test_get_all_vehicles_empty(self, client, db_session):
        """Test getting all vehicles when database is empty"""
        response = client.get("/api/vehicles/")
        assert response.status_code == 200
        assert response.json() == []
    
    def test_get_all_vehicles_with_data(self, client, db_session, sample_vehicles):
        """Test getting all vehicles with sample data"""
        response = client.get("/api/vehicles/")
        assert response.status_code == 200
        
        data = response.json()
        assert len(data) == 3
        
        # Check first vehicle
        vehicle = data[0]
        assert vehicle["id"] == 1
        assert vehicle["registration"] == "ABC123"
        assert vehicle["make"] == "Toyota"
        assert vehicle["color"] == "Red"
        assert "created_at" in vehicle
        assert "updated_at" in vehicle
    
    def test_get_available_vehicles_no_filters(self, client, db_session, sample_vehicles, sample_availability):
        """Test getting available vehicles for a future date range"""
        today = date.today()
        start_date = today + timedelta(days=5)
        end_date = today + timedelta(days=7)
        
        response = client.get(f"/api/vehicles/available?start_date={start_date}&end_date={end_date}")
        assert response.status_code == 200
        
        data = response.json()
        # Should return vehicles 1 and 2 (vehicle 3 is not available)
        assert len(data) == 2
        registrations = [v["registration"] for v in data]
        assert "ABC123" in registrations
        assert "DEF456" in registrations
        assert "GHI789" not in registrations
    
    def test_get_available_vehicles_with_booking_conflict(self, client, db_session, sample_vehicles, sample_bookings, sample_availability):
        """Test getting available vehicles when there's a booking conflict"""
        today = date.today()
        # Request dates that overlap with existing booking for vehicle 1
        start_date = today + timedelta(days=1)
        end_date = today + timedelta(days=2)
        
        response = client.get(f"/api/vehicles/available?start_date={start_date}&end_date={end_date}")
        assert response.status_code == 200
        
        data = response.json()
        # Should only return vehicle 2 (vehicle 1 has booking, vehicle 3 is not available)
        assert len(data) == 1
        assert data[0]["registration"] == "DEF456"
    
    def test_get_available_vehicles_invalid_date_range(self, client, db_session):
        """Test getting available vehicles with invalid date range"""
        today = date.today()
        start_date = today + timedelta(days=5)
        end_date = today + timedelta(days=2)  # End before start
        
        response = client.get(f"/api/vehicles/available?start_date={start_date}&end_date={end_date}")
        assert response.status_code == 400
        response_data = response.json()
        assert "Start date must be before or equal to end date" in response_data["message"]
    
    def test_get_available_vehicles_past_date(self, client, db_session):
        """Test getting available vehicles with past start date"""
        today = date.today()
        start_date = today - timedelta(days=1)  # Yesterday
        end_date = today + timedelta(days=1)
        
        response = client.get(f"/api/vehicles/available?start_date={start_date}&end_date={end_date}")
        assert response.status_code == 400
        response_data = response.json()
        assert "Start date cannot be in the past" in response_data["message"]
    
    def test_get_available_vehicles_missing_parameters(self, client, db_session):
        """Test getting available vehicles without required parameters"""
        response = client.get("/api/vehicles/available")
        assert response.status_code == 422  # Validation error


class TestVehicleService:
    """Test cases for VehicleService business logic"""
    
    def test_get_all_vehicles_service(self, db_session, sample_vehicles):
        """Test VehicleService.get_all_vehicles method"""
        vehicles = VehicleService.get_all_vehicles(db_session)
        assert len(vehicles) == 3
        assert vehicles[0].registration == "ABC123"
    
    def test_get_available_vehicles_service(self, db_session, sample_vehicles, sample_availability):
        """Test VehicleService.get_available_vehicles method"""
        today = date.today()
        start_date = today + timedelta(days=5)
        end_date = today + timedelta(days=7)
        
        vehicles = VehicleService.get_available_vehicles(db_session, start_date, end_date)
        assert len(vehicles) == 2  # Vehicles 1 and 2 should be available
        registrations = [v.registration for v in vehicles]
        assert "ABC123" in registrations
        assert "DEF456" in registrations
        assert "GHI789" not in registrations
    
    def test_is_vehicle_available_no_conflicts(self, db_session, sample_vehicles, sample_availability):
        """Test _is_vehicle_available with no conflicts"""
        today = date.today()
        start_date = today + timedelta(days=5)
        end_date = today + timedelta(days=7)
        
        # Vehicle 1 should be available
        is_available = VehicleService._is_vehicle_available(db_session, 1, start_date, end_date)
        assert is_available is True
        
        # Vehicle 3 should not be available (marked as unavailable in seed data)
        is_available = VehicleService._is_vehicle_available(db_session, 3, start_date, end_date)
        assert is_available is False
    
    def test_is_vehicle_available_with_booking_conflict(self, db_session, sample_vehicles, sample_bookings, sample_availability):
        """Test _is_vehicle_available with booking conflicts"""
        today = date.today()
        # Dates that overlap with existing booking for vehicle 1
        start_date = today + timedelta(days=1)
        end_date = today + timedelta(days=2)
        
        # Vehicle 1 should not be available due to booking
        is_available = VehicleService._is_vehicle_available(db_session, 1, start_date, end_date)
        assert is_available is False
        
        # Vehicle 2 should be available (no booking conflict)
        is_available = VehicleService._is_vehicle_available(db_session, 2, start_date, end_date)
        assert is_available is True
    
    def test_is_vehicle_available_edge_case_same_day(self, db_session, sample_vehicles, sample_availability):
        """Test _is_vehicle_available for same day booking"""
        today = date.today()
        start_date = today + timedelta(days=5)
        end_date = today + timedelta(days=5)  # Same day
        
        is_available = VehicleService._is_vehicle_available(db_session, 1, start_date, end_date)
        assert is_available is True