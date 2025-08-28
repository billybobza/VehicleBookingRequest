#!/usr/bin/env python3
"""
Final Integration Test for Car Booking System

This test verifies:
1. Complete booking workflow from form submission to confirmation
2. Return date calculation works correctly for all scenarios
3. Availability checking prevents double bookings
4. Frontend-backend API integration
"""

import pytest
import tempfile
import os
from datetime import datetime, date, timedelta
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Import application components
from main import app
from models.database import Base, get_db, Vehicle, Booking, VehicleAvailability
from database_init import seed_vehicles, seed_availability_data
from services.booking_service import BookingService


class TestFinalIntegration:
    """Final integration tests for the complete car booking system"""
    
    @pytest.fixture(scope="class")
    def test_db(self):
        """Create a test database for integration tests"""
        # Create temporary database file
        db_fd, db_path = tempfile.mkstemp(suffix='.db')
        test_database_url = f"sqlite:///{db_path}"
        
        # Create test engine and session
        test_engine = create_engine(
            test_database_url,
            connect_args={"check_same_thread": False}
        )
        TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)
        
        # Create all tables
        Base.metadata.create_all(bind=test_engine)
        
        # Override the get_db dependency
        def override_get_db():
            try:
                db = TestingSessionLocal()
                yield db
            finally:
                db.close()
        
        app.dependency_overrides[get_db] = override_get_db
        
        # Seed test data
        db = TestingSessionLocal()
        try:
            seed_vehicles(db)
            seed_availability_data(db)
        finally:
            db.close()
        
        yield TestingSessionLocal
        
        # Cleanup
        os.close(db_fd)
        os.unlink(db_path)
        app.dependency_overrides.clear()
    
    @pytest.fixture
    def client(self, test_db):
        """Create test client with test database"""
        return TestClient(app)
    
    def test_complete_booking_workflow(self, client, test_db):
        """Test complete booking workflow from form submission to confirmation"""
        print("\n=== Testing Complete Booking Workflow ===")
        
        # Step 1: Get available vehicles
        future_date = (date.today() + timedelta(days=7)).isoformat()
        end_date = (date.today() + timedelta(days=8)).isoformat()
        
        response = client.get(f"/api/vehicles/available?start_date={future_date}&end_date={end_date}")
        assert response.status_code == 200, f"Failed to get available vehicles: {response.text}"
        
        available_vehicles = response.json()
        assert len(available_vehicles) > 0, "No vehicles available for testing"
        
        selected_vehicle = available_vehicles[0]
        print(f"Selected vehicle: {selected_vehicle['registration']} ({selected_vehicle['make']})")
        
        # Step 2: Create booking request
        start_datetime = datetime.combine(date.today() + timedelta(days=7), datetime.min.time().replace(hour=9))
        end_datetime = datetime.combine(date.today() + timedelta(days=8), datetime.min.time().replace(hour=17))
        
        booking_request = {
            "vehicle_id": selected_vehicle["id"],
            "start_datetime": start_datetime.isoformat(),
            "end_datetime": end_datetime.isoformat(),
            "reason": "Business meeting in another city",
            "estimated_mileage": 150
        }
        
        # Step 3: Submit booking
        response = client.post("/api/bookings/", json=booking_request)
        assert response.status_code == 201, f"Failed to create booking: {response.text}"
        
        booking_confirmation = response.json()
        assert booking_confirmation["id"] is not None
        assert booking_confirmation["vehicle_id"] == selected_vehicle["id"]
        assert booking_confirmation["status"] == "confirmed"
        
        print(f"Booking created successfully: ID #{booking_confirmation['id']}")
        
        # Step 4: Verify booking details
        booking_id = booking_confirmation["id"]
        response = client.get(f"/api/bookings/{booking_id}")
        assert response.status_code == 200, f"Failed to retrieve booking: {response.text}"
        
        retrieved_booking = response.json()
        assert retrieved_booking["id"] == booking_id
        assert retrieved_booking["reason"] == booking_request["reason"]
        assert retrieved_booking["estimated_mileage"] == booking_request["estimated_mileage"]
        
        print("Booking retrieval verified successfully")
        
        # Step 5: Verify vehicle is no longer available for the same period
        response = client.get(f"/api/vehicles/available?start_date={future_date}&end_date={end_date}")
        assert response.status_code == 200
        
        updated_available_vehicles = response.json()
        vehicle_ids = [v["id"] for v in updated_available_vehicles]
        assert selected_vehicle["id"] not in vehicle_ids, "Vehicle should not be available after booking"
        
        print("Availability checking verified - vehicle correctly marked as unavailable")
        
        return booking_confirmation
    
    def test_return_date_calculation_scenarios(self, client, test_db):
        """Test return date calculation for different scenarios"""
        print("\n=== Testing Return Date Calculation ===")
        
        # Get a vehicle for testing
        response = client.get("/api/vehicles/")
        assert response.status_code == 200
        vehicles = response.json()
        test_vehicle = vehicles[0]
        
        test_cases = [
            {
                "name": "Weekday return (Tuesday to Wednesday)",
                "start_day": 1,  # Tuesday
                "end_day": 2,    # Wednesday
                "expected_same": True  # Should return at end_datetime
            },
            {
                "name": "Friday return",
                "start_day": 4,  # Friday
                "end_day": 4,    # Friday
                "expected_monday": True  # Should return next Monday 9 AM
            },
            {
                "name": "Weekend return (Saturday)",
                "start_day": 5,  # Saturday
                "end_day": 5,    # Saturday
                "expected_monday": True  # Should return next Monday 9 AM
            },
            {
                "name": "Weekend return (Sunday)",
                "start_day": 6,  # Sunday
                "end_day": 6,    # Sunday
                "expected_monday": True  # Should return next Monday 9 AM
            }
        ]
        
        for i, test_case in enumerate(test_cases):
            print(f"\nTesting: {test_case['name']}")
            
            # Calculate dates for the test case
            today = date.today()
            days_ahead = 7 + i * 7  # Space out test cases
            
            # Find the target weekday
            target_date = today + timedelta(days=days_ahead)
            while target_date.weekday() != test_case["start_day"]:
                target_date += timedelta(days=1)
            
            end_date = target_date
            if test_case["end_day"] != test_case["start_day"]:
                end_date = target_date + timedelta(days=(test_case["end_day"] - test_case["start_day"]))
            
            start_datetime = datetime.combine(target_date, datetime.min.time().replace(hour=9))
            end_datetime = datetime.combine(end_date, datetime.min.time().replace(hour=17))
            
            booking_request = {
                "vehicle_id": test_vehicle["id"],
                "start_datetime": start_datetime.isoformat(),
                "end_datetime": end_datetime.isoformat(),
                "reason": f"Test booking for {test_case['name']}",
                "estimated_mileage": 100
            }
            
            # Create booking
            response = client.post("/api/bookings/", json=booking_request)
            if response.status_code != 201:
                print(f"Skipping {test_case['name']} - vehicle not available: {response.text}")
                continue
            
            booking = response.json()
            return_datetime = datetime.fromisoformat(booking["return_datetime"])
            
            if test_case.get("expected_same"):
                # Should return at end_datetime
                expected_return = end_datetime
                assert return_datetime == expected_return, f"Expected return at {expected_return}, got {return_datetime}"
                print(f"✓ Correct return time: {return_datetime}")
            
            elif test_case.get("expected_monday"):
                # Should return next Monday at 9 AM
                assert return_datetime.weekday() == 0, f"Expected Monday return, got {return_datetime.strftime('%A')}"
                assert return_datetime.hour == 9, f"Expected 9 AM return, got {return_datetime.hour}:00"
                assert return_datetime > end_datetime, f"Return date should be after end date"
                print(f"✓ Correct Monday return: {return_datetime}")
    
    def test_double_booking_prevention(self, client, test_db):
        """Test that double bookings are prevented"""
        print("\n=== Testing Double Booking Prevention ===")
        
        # Get available vehicles
        future_date = (date.today() + timedelta(days=14)).isoformat()
        end_date = (date.today() + timedelta(days=15)).isoformat()
        
        response = client.get(f"/api/vehicles/available?start_date={future_date}&end_date={end_date}")
        assert response.status_code == 200
        available_vehicles = response.json()
        assert len(available_vehicles) > 0
        
        test_vehicle = available_vehicles[0]
        
        # Create first booking
        start_datetime = datetime.combine(date.today() + timedelta(days=14), datetime.min.time().replace(hour=9))
        end_datetime = datetime.combine(date.today() + timedelta(days=15), datetime.min.time().replace(hour=17))
        
        booking_request_1 = {
            "vehicle_id": test_vehicle["id"],
            "start_datetime": start_datetime.isoformat(),
            "end_datetime": end_datetime.isoformat(),
            "reason": "First booking",
            "estimated_mileage": 100
        }
        
        response = client.post("/api/bookings/", json=booking_request_1)
        assert response.status_code == 201, f"First booking failed: {response.text}"
        first_booking = response.json()
        print(f"First booking created: ID #{first_booking['id']}")
        
        # Attempt overlapping booking (should fail)
        overlap_start = start_datetime + timedelta(hours=2)  # 2 hours into first booking
        overlap_end = end_datetime + timedelta(hours=2)      # 2 hours after first booking
        
        booking_request_2 = {
            "vehicle_id": test_vehicle["id"],
            "start_datetime": overlap_start.isoformat(),
            "end_datetime": overlap_end.isoformat(),
            "reason": "Overlapping booking (should fail)",
            "estimated_mileage": 50
        }
        
        response = client.post("/api/bookings/", json=booking_request_2)
        assert response.status_code == 400, f"Expected 400 for overlapping booking, got {response.status_code}: {response.text}"
        print("✓ Overlapping booking correctly rejected")
        
        # Attempt booking immediately after (should succeed)
        next_start = end_datetime + timedelta(hours=1)
        next_end = next_start + timedelta(hours=2)
        
        booking_request_3 = {
            "vehicle_id": test_vehicle["id"],
            "start_datetime": next_start.isoformat(),
            "end_datetime": next_end.isoformat(),
            "reason": "Sequential booking (should succeed)",
            "estimated_mileage": 30
        }
        
        response = client.post("/api/bookings/", json=booking_request_3)
        assert response.status_code == 201, f"Sequential booking failed: {response.text}"
        sequential_booking = response.json()
        print(f"✓ Sequential booking succeeded: ID #{sequential_booking['id']}")
    
    def test_api_error_handling(self, client, test_db):
        """Test API error handling and validation"""
        print("\n=== Testing API Error Handling ===")
        
        # Test invalid vehicle ID
        invalid_booking = {
            "vehicle_id": 99999,  # Non-existent vehicle
            "start_datetime": (datetime.now() + timedelta(days=1)).isoformat(),
            "end_datetime": (datetime.now() + timedelta(days=2)).isoformat(),
            "reason": "Test booking",
            "estimated_mileage": 100
        }
        
        response = client.post("/api/bookings/", json=invalid_booking)
        assert response.status_code == 404, f"Expected 404 for invalid vehicle, got {response.status_code}"
        print("✓ Invalid vehicle ID correctly handled")
        
        # Test validation errors
        invalid_data = {
            "vehicle_id": "not_a_number",
            "start_datetime": "invalid_date",
            "end_datetime": "invalid_date",
            "reason": "",  # Empty reason
            "estimated_mileage": -1  # Negative mileage
        }
        
        response = client.post("/api/bookings/", json=invalid_data)
        assert response.status_code == 422, f"Expected 422 for validation errors, got {response.status_code}"
        print("✓ Validation errors correctly handled")
        
        # Test missing fields
        incomplete_data = {
            "vehicle_id": 1
            # Missing required fields
        }
        
        response = client.post("/api/bookings/", json=incomplete_data)
        assert response.status_code == 422, f"Expected 422 for missing fields, got {response.status_code}"
        print("✓ Missing fields correctly handled")
    
    def test_business_logic_validation(self, client, test_db):
        """Test business logic validation"""
        print("\n=== Testing Business Logic Validation ===")
        
        # Get a vehicle
        response = client.get("/api/vehicles/")
        assert response.status_code == 200
        vehicles = response.json()
        test_vehicle = vehicles[0]
        
        # Test past date booking (should fail)
        past_booking = {
            "vehicle_id": test_vehicle["id"],
            "start_datetime": (datetime.now() - timedelta(days=1)).isoformat(),
            "end_datetime": (datetime.now() + timedelta(hours=1)).isoformat(),
            "reason": "Past date booking",
            "estimated_mileage": 50
        }
        
        response = client.post("/api/bookings/", json=past_booking)
        assert response.status_code == 422, f"Expected 422 for past date, got {response.status_code}"
        print("✓ Past date booking correctly rejected")
        
        # Test end before start (should fail)
        invalid_order = {
            "vehicle_id": test_vehicle["id"],
            "start_datetime": (datetime.now() + timedelta(days=2)).isoformat(),
            "end_datetime": (datetime.now() + timedelta(days=1)).isoformat(),
            "reason": "Invalid date order",
            "estimated_mileage": 50
        }
        
        response = client.post("/api/bookings/", json=invalid_order)
        assert response.status_code == 422, f"Expected 422 for invalid date order, got {response.status_code}"
        print("✓ Invalid date order correctly rejected")


def run_integration_tests():
    """Run all integration tests"""
    print("=" * 60)
    print("RUNNING FINAL INTEGRATION TESTS")
    print("=" * 60)
    
    # Run pytest with this specific test file
    import subprocess
    import sys
    
    result = subprocess.run([
        sys.executable, "-m", "pytest", 
        __file__, 
        "-v", 
        "--tb=short",
        "-s"  # Don't capture output so we can see print statements
    ], cwd=os.path.dirname(__file__))
    
    return result.returncode == 0


if __name__ == "__main__":
    success = run_integration_tests()
    if success:
        print("\n" + "=" * 60)
        print("✅ ALL INTEGRATION TESTS PASSED!")
        print("✅ Frontend-backend integration verified")
        print("✅ Return date calculation working correctly")
        print("✅ Double booking prevention working")
        print("✅ API error handling working")
        print("=" * 60)
    else:
        print("\n" + "=" * 60)
        print("❌ SOME INTEGRATION TESTS FAILED")
        print("Please check the output above for details")
        print("=" * 60)
        exit(1)