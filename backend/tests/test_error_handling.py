import pytest
from fastapi.testclient import TestClient
from fastapi import HTTPException
from main import app

client = TestClient(app)


def test_http_exception_handling():
    """Test HTTP exception handling"""
    # Test 501 Not Implemented from booking endpoint
    response = client.post("/api/bookings/", json={
        "vehicle_id": 1,
        "start_datetime": "2025-12-01T10:00:00",
        "end_datetime": "2025-12-01T12:00:00", 
        "reason": "Test booking",
        "estimated_mileage": 100
    })
    
    assert response.status_code == 501
    json_response = response.json()
    assert "error" in json_response
    assert json_response["error"] == "HTTP_ERROR"
    assert "message" in json_response


def test_validation_error_structure():
    """Test that validation errors have the correct structure"""
    # Send invalid booking data
    invalid_data = {
        "vehicle_id": "not_a_number",
        "start_datetime": "not_a_date",
        "end_datetime": "not_a_date",
        "reason": "",  # Empty reason should fail validation
        "estimated_mileage": -5  # Negative mileage should fail validation
    }
    
    response = client.post("/api/bookings/", json=invalid_data)
    
    assert response.status_code == 422
    json_response = response.json()
    
    # Check error structure
    assert "error" in json_response
    assert "message" in json_response
    assert "details" in json_response
    assert json_response["error"] == "VALIDATION_ERROR"
    assert isinstance(json_response["details"], list)


def test_missing_required_fields():
    """Test validation when required fields are missing"""
    incomplete_data = {
        "vehicle_id": 1,
        # Missing required fields
    }
    
    response = client.post("/api/bookings/", json=incomplete_data)
    
    assert response.status_code == 422
    json_response = response.json()
    assert json_response["error"] == "VALIDATION_ERROR"
    
    # Should have details about missing fields
    details = json_response["details"]
    missing_fields = [error["loc"][-1] for error in details if error["type"] == "missing"]
    
    expected_missing = ["start_datetime", "end_datetime", "reason", "estimated_mileage"]
    for field in expected_missing:
        assert field in missing_fields


def test_endpoint_not_found():
    """Test 404 handling for non-existent endpoints"""
    response = client.get("/api/nonexistent")
    assert response.status_code == 404


def test_method_not_allowed():
    """Test 405 handling for wrong HTTP methods"""
    # Try to POST to a GET-only endpoint
    response = client.post("/api/vehicles/")
    assert response.status_code == 405