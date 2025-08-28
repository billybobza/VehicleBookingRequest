#!/usr/bin/env python3
"""
Simple test script to verify admin endpoints are working
"""

import requests
import json
from datetime import date, timedelta

BASE_URL = "http://localhost:8000/api/admin"

def test_dashboard_stats():
    """Test dashboard stats endpoint"""
    print("Testing dashboard stats...")
    response = requests.get(f"{BASE_URL}/dashboard/stats")
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Dashboard stats: {json.dumps(data, indent=2)}")
    else:
        print(f"Error: {response.text}")
    print()

def test_get_vehicles():
    """Test get all vehicles endpoint"""
    print("Testing get all vehicles...")
    response = requests.get(f"{BASE_URL}/vehicles/")
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Found {len(data)} vehicles")
        for vehicle in data[:3]:  # Show first 3
            print(f"  - {vehicle['registration']} ({vehicle['make']}, {vehicle['color']})")
    else:
        print(f"Error: {response.text}")
    print()

def test_create_vehicle():
    """Test create vehicle endpoint"""
    print("Testing create vehicle...")
    vehicle_data = {
        "registration": "TEST123",
        "make": "Test Vehicle",
        "color": "Test Color"
    }
    
    response = requests.post(
        f"{BASE_URL}/vehicles/",
        json=vehicle_data,
        headers={"Content-Type": "application/json"}
    )
    
    print(f"Status: {response.status_code}")
    if response.status_code == 201:
        data = response.json()
        print(f"Created vehicle: {data['registration']} (ID: {data['id']})")
        return data['id']
    else:
        print(f"Error: {response.text}")
        return None
    print()

def test_get_bookings():
    """Test get all bookings endpoint"""
    print("Testing get all bookings...")
    response = requests.get(f"{BASE_URL}/bookings/")
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Found {len(data)} bookings")
        for booking in data[:3]:  # Show first 3
            print(f"  - Booking #{booking['id']} for {booking['vehicle']['registration']} ({booking['status']})")
    else:
        print(f"Error: {response.text}")
    print()

def cleanup_test_vehicle(vehicle_id):
    """Clean up test vehicle"""
    if vehicle_id:
        print(f"Cleaning up test vehicle {vehicle_id}...")
        response = requests.delete(f"{BASE_URL}/vehicles/{vehicle_id}")
        print(f"Cleanup status: {response.status_code}")
        print()

def main():
    """Run all tests"""
    print("🔧 Testing Admin API Endpoints")
    print("=" * 50)
    
    try:
        # Test dashboard
        test_dashboard_stats()
        
        # Test vehicles
        test_get_vehicles()
        
        # Test create vehicle
        vehicle_id = test_create_vehicle()
        
        # Test bookings
        test_get_bookings()
        
        # Cleanup
        cleanup_test_vehicle(vehicle_id)
        
        print("✅ All tests completed!")
        
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to the server. Make sure the backend is running on http://localhost:8000")
    except Exception as e:
        print(f"❌ Test failed with error: {e}")

if __name__ == "__main__":
    main()