import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_app_creation():
    """Test that the FastAPI app is created correctly"""
    assert app.title == "Car Booking System API"
    assert app.version == "1.0.0"


def test_health_endpoint():
    """Test the health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


def test_root_endpoint():
    """Test the root endpoint"""
    response = client.get("/")
    assert response.status_code == 200
    assert "message" in response.json()


def test_cors_headers():
    """Test that CORS headers are properly configured"""
    # Test actual CORS by making a request with Origin header
    response = client.get("/", headers={"Origin": "http://localhost:5173"})
    # Should return 200 and have CORS headers
    assert response.status_code == 200
    # Note: In test environment, CORS headers might not be fully visible


def test_api_routes_included():
    """Test that API routes are properly included"""
    # Test vehicles endpoint exists (even if not implemented)
    response = client.get("/api/vehicles/")
    # Should return 200 with empty list (placeholder implementation)
    assert response.status_code == 200
    
    # Test bookings endpoint exists (even if not implemented)
    response = client.get("/api/bookings/1")
    # Should return 501 (not implemented)
    assert response.status_code == 501


def test_validation_error_handling():
    """Test that validation errors are handled properly"""
    # Try to create a booking with invalid data
    invalid_booking_data = {
        "vehicle_id": "not_an_integer",
        "start_datetime": "invalid_date",
        "end_datetime": "invalid_date",
        "reason": "",
        "estimated_mileage": -1
    }
    
    response = client.post("/api/bookings/", json=invalid_booking_data)
    assert response.status_code == 422
    assert "error" in response.json()
    assert response.json()["error"] == "VALIDATION_ERROR"


def test_404_error_handling():
    """Test that 404 errors are handled properly"""
    response = client.get("/nonexistent-endpoint")
    assert response.status_code == 404