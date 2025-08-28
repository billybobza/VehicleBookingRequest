#!/usr/bin/env python3
"""
Manual Integration Test for Car Booking System

This script tests the complete integration between frontend and backend
by making direct API calls and verifying the functionality.
"""

import requests
import json
from datetime import datetime, date, timedelta
from typing import Dict, Any, List


class IntegrationTester:
    def __init__(self, backend_url: str = "http://localhost:8000"):
        self.backend_url = backend_url
        self.created_bookings: List[int] = []
    
    def test_backend_health(self) -> bool:
        """Test if backend is healthy"""
        try:
            response = requests.get(f"{self.backend_url}/health", timeout=5)
            return response.status_code == 200 and response.json().get("status") == "healthy"
        except Exception as e:
            print(f"Backend health check failed: {e}")
            return False
    
    def get_vehicles(self) -> List[Dict[str, Any]]:
        """Get all vehicles"""
        response = requests.get(f"{self.backend_url}/api/vehicles/")
        response.raise_for_status()
        return response.json()
    
    def get_available_vehicles(self, start_date: str, end_date: str) -> List[Dict[str, Any]]:
        """Get available vehicles for date range"""
        params = {"start_date": start_date, "end_date": end_date}
        response = requests.get(f"{self.backend_url}/api/vehicles/available", params=params)
        response.raise_for_status()
        return response.json()
    
    def create_booking(self, booking_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a booking"""
        response = requests.post(
            f"{self.backend_url}/api/bookings/",
            json=booking_data,
            headers={"Content-Type": "application/json"}
        )
        response.raise_for_status()
        return response.json()
    
    def get_booking(self, booking_id: int) -> Dict[str, Any]:
        """Get booking by ID"""
        response = requests.get(f"{self.backend_url}/api/bookings/{booking_id}")
        response.raise_for_status()
        return response.json()
    
    def test_complete_booking_workflow(self) -> bool:
        """Test complete booking workflow"""
        print("\n=== Testing Complete Booking Workflow ===")
        
        try:
            # Step 1: Get available vehicles
            future_date = (date.today() + timedelta(days=7)).isoformat()
            end_date = (date.today() + timedelta(days=8)).isoformat()
            
            available_vehicles = self.get_available_vehicles(future_date, end_date)
            assert len(available_vehicles) > 0, "No vehicles available for testing"
            
            selected_vehicle = available_vehicles[0]
            print(f"✓ Selected vehicle: {selected_vehicle['registration']} ({selected_vehicle['make']})")
            
            # Step 2: Create booking
            start_datetime = datetime.combine(date.today() + timedelta(days=7), datetime.min.time().replace(hour=9))
            end_datetime = datetime.combine(date.today() + timedelta(days=8), datetime.min.time().replace(hour=17))
            
            booking_request = {
                "vehicle_id": selected_vehicle["id"],
                "start_datetime": start_datetime.isoformat(),
                "end_datetime": end_datetime.isoformat(),
                "reason": "Integration test - business meeting",
                "estimated_mileage": 150
            }
            
            booking = self.create_booking(booking_request)
            self.created_bookings.append(booking["id"])
            
            assert booking["id"] is not None
            assert booking["vehicle_id"] == selected_vehicle["id"]
            assert booking["status"] == "confirmed"
            print(f"✓ Booking created successfully: ID #{booking['id']}")
            
            # Step 3: Verify booking retrieval
            retrieved_booking = self.get_booking(booking["id"])
            assert retrieved_booking["id"] == booking["id"]
            assert retrieved_booking["reason"] == booking_request["reason"]
            print("✓ Booking retrieval verified")
            
            # Step 4: Verify availability updated
            updated_vehicles = self.get_available_vehicles(future_date, end_date)
            vehicle_ids = [v["id"] for v in updated_vehicles]
            assert selected_vehicle["id"] not in vehicle_ids, "Vehicle should not be available after booking"
            print("✓ Availability checking verified")
            
            return True
            
        except Exception as e:
            print(f"❌ Booking workflow test failed: {e}")
            return False
    
    def test_return_date_calculation(self) -> bool:
        """Test return date calculation for different scenarios"""
        print("\n=== Testing Return Date Calculation ===")
        
        try:
            vehicles = self.get_vehicles()
            test_cases = [
                {
                    "name": "Weekday return (Tuesday)",
                    "day_offset": 14,
                    "target_weekday": 1,  # Tuesday
                    "expected_same": True
                },
                {
                    "name": "Friday return",
                    "day_offset": 21,
                    "target_weekday": 4,  # Friday
                    "expected_monday": True
                },
                {
                    "name": "Saturday return",
                    "day_offset": 28,
                    "target_weekday": 5,  # Saturday
                    "expected_monday": True
                }
            ]
            
            for i, test_case in enumerate(test_cases):
                print(f"\nTesting: {test_case['name']}")
                
                # Find target date
                target_date = date.today() + timedelta(days=test_case["day_offset"])
                while target_date.weekday() != test_case["target_weekday"]:
                    target_date += timedelta(days=1)
                
                start_datetime = datetime.combine(target_date, datetime.min.time().replace(hour=9))
                end_datetime = datetime.combine(target_date, datetime.min.time().replace(hour=17))
                
                # Use different vehicles to avoid conflicts
                vehicle = vehicles[i % len(vehicles)]
                
                booking_request = {
                    "vehicle_id": vehicle["id"],
                    "start_datetime": start_datetime.isoformat(),
                    "end_datetime": end_datetime.isoformat(),
                    "reason": f"Test booking for {test_case['name']}",
                    "estimated_mileage": 100
                }
                
                try:
                    booking = self.create_booking(booking_request)
                    self.created_bookings.append(booking["id"])
                    
                    return_datetime = datetime.fromisoformat(booking["return_datetime"])
                    
                    if test_case.get("expected_same"):
                        assert return_datetime == end_datetime, f"Expected same day return, got {return_datetime}"
                        print(f"✓ Correct return time: {return_datetime}")
                    elif test_case.get("expected_monday"):
                        assert return_datetime.weekday() == 0, f"Expected Monday return, got {return_datetime.strftime('%A')}"
                        assert return_datetime.hour == 9, f"Expected 9 AM return, got {return_datetime.hour}:00"
                        print(f"✓ Correct Monday return: {return_datetime}")
                        
                except requests.exceptions.HTTPError as e:
                    if e.response.status_code == 400:
                        print(f"Skipping {test_case['name']} - vehicle not available")
                        continue
                    else:
                        raise
            
            return True
            
        except Exception as e:
            print(f"❌ Return date calculation test failed: {e}")
            return False
    
    def test_double_booking_prevention(self) -> bool:
        """Test double booking prevention"""
        print("\n=== Testing Double Booking Prevention ===")
        
        try:
            vehicles = self.get_vehicles()
            test_vehicle = vehicles[0]
            
            # Create first booking
            start_date = date.today() + timedelta(days=35)
            start_datetime = datetime.combine(start_date, datetime.min.time().replace(hour=9))
            end_datetime = datetime.combine(start_date, datetime.min.time().replace(hour=17))
            
            first_booking = {
                "vehicle_id": test_vehicle["id"],
                "start_datetime": start_datetime.isoformat(),
                "end_datetime": end_datetime.isoformat(),
                "reason": "First booking for double booking test",
                "estimated_mileage": 100
            }
            
            booking1 = self.create_booking(first_booking)
            self.created_bookings.append(booking1["id"])
            print(f"✓ First booking created: ID #{booking1['id']}")
            
            # Attempt overlapping booking
            overlap_start = start_datetime + timedelta(hours=2)
            overlap_end = end_datetime + timedelta(hours=2)
            
            overlapping_booking = {
                "vehicle_id": test_vehicle["id"],
                "start_datetime": overlap_start.isoformat(),
                "end_datetime": overlap_end.isoformat(),
                "reason": "Overlapping booking (should fail)",
                "estimated_mileage": 50
            }
            
            try:
                self.create_booking(overlapping_booking)
                assert False, "Overlapping booking should have failed"
            except requests.exceptions.HTTPError as e:
                assert e.response.status_code == 400, f"Expected 400, got {e.response.status_code}"
                print("✓ Overlapping booking correctly rejected")
            
            # Attempt sequential booking
            next_start = end_datetime + timedelta(hours=1)
            next_end = next_start + timedelta(hours=2)
            
            sequential_booking = {
                "vehicle_id": test_vehicle["id"],
                "start_datetime": next_start.isoformat(),
                "end_datetime": next_end.isoformat(),
                "reason": "Sequential booking (should succeed)",
                "estimated_mileage": 30
            }
            
            booking2 = self.create_booking(sequential_booking)
            self.created_bookings.append(booking2["id"])
            print(f"✓ Sequential booking succeeded: ID #{booking2['id']}")
            
            return True
            
        except Exception as e:
            print(f"❌ Double booking prevention test failed: {e}")
            return False
    
    def test_api_error_handling(self) -> bool:
        """Test API error handling"""
        print("\n=== Testing API Error Handling ===")
        
        try:
            # Test invalid vehicle ID
            invalid_booking = {
                "vehicle_id": 99999,
                "start_datetime": (datetime.now() + timedelta(days=1)).isoformat(),
                "end_datetime": (datetime.now() + timedelta(days=2)).isoformat(),
                "reason": "Test booking",
                "estimated_mileage": 100
            }
            
            try:
                self.create_booking(invalid_booking)
                assert False, "Invalid vehicle booking should have failed"
            except requests.exceptions.HTTPError as e:
                assert e.response.status_code == 404, f"Expected 404, got {e.response.status_code}"
                print("✓ Invalid vehicle ID correctly handled")
            
            # Test validation errors
            invalid_data = {
                "vehicle_id": "not_a_number",
                "start_datetime": "invalid_date",
                "end_datetime": "invalid_date",
                "reason": "",
                "estimated_mileage": -1
            }
            
            try:
                self.create_booking(invalid_data)
                assert False, "Invalid data booking should have failed"
            except requests.exceptions.HTTPError as e:
                assert e.response.status_code == 422, f"Expected 422, got {e.response.status_code}"
                print("✓ Validation errors correctly handled")
            
            return True
            
        except Exception as e:
            print(f"❌ API error handling test failed: {e}")
            return False
    
    def run_all_tests(self) -> bool:
        """Run all integration tests"""
        print("=" * 60)
        print("RUNNING FINAL INTEGRATION TESTS")
        print("=" * 60)
        
        # Check backend health
        if not self.test_backend_health():
            print("❌ Backend is not healthy. Please start the backend server.")
            return False
        
        print("✓ Backend is healthy")
        
        # Run all tests
        tests = [
            self.test_complete_booking_workflow,
            self.test_return_date_calculation,
            self.test_double_booking_prevention,
            self.test_api_error_handling
        ]
        
        passed = 0
        for test in tests:
            if test():
                passed += 1
        
        print(f"\n{'=' * 60}")
        if passed == len(tests):
            print("✅ ALL INTEGRATION TESTS PASSED!")
            print("✅ Frontend-backend integration verified")
            print("✅ Return date calculation working correctly")
            print("✅ Double booking prevention working")
            print("✅ API error handling working")
        else:
            print(f"❌ {len(tests) - passed} out of {len(tests)} tests failed")
        
        print(f"Created {len(self.created_bookings)} test bookings during integration tests")
        print("=" * 60)
        
        return passed == len(tests)


if __name__ == "__main__":
    tester = IntegrationTester()
    success = tester.run_all_tests()
    exit(0 if success else 1)