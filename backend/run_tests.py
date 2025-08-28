#!/usr/bin/env python3
"""
Comprehensive test runner for the car booking system backend.
Runs all test suites and generates coverage reports.
"""

import subprocess
import sys
import os
from pathlib import Path


def run_command(command, description):
    """Run a command and handle errors"""
    print(f"\n{'='*60}")
    print(f"Running: {description}")
    print(f"Command: {command}")
    print(f"{'='*60}")
    
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(result.stdout)
        if result.stderr:
            print("STDERR:", result.stderr)
        return True
    except subprocess.CalledProcessError as e:
        print(f"ERROR: {description} failed with exit code {e.returncode}")
        print("STDOUT:", e.stdout)
        print("STDERR:", e.stderr)
        return False


def main():
    """Run all test suites"""
    print("Car Booking System - Comprehensive Test Suite")
    print("=" * 60)
    
    # Change to backend directory
    backend_dir = Path(__file__).parent
    os.chdir(backend_dir)
    
    # Test commands to run
    test_commands = [
        {
            "command": "python -m pytest tests/test_api_setup.py -v",
            "description": "API Setup Tests"
        },
        {
            "command": "python -m pytest tests/test_vehicle_endpoints.py -v",
            "description": "Vehicle Endpoint Tests"
        },
        {
            "command": "python -m pytest tests/test_booking_endpoints.py -v",
            "description": "Booking Endpoint Tests"
        },
        {
            "command": "python -m pytest tests/test_error_handling.py -v",
            "description": "Error Handling Tests"
        },
        {
            "command": "python -m pytest tests/test_business_logic.py -v",
            "description": "Business Logic Unit Tests"
        },
        {
            "command": "python -m pytest tests/test_integration.py -v",
            "description": "Integration Tests"
        },
        {
            "command": "python -m pytest tests/test_edge_cases.py -v",
            "description": "Edge Cases and Boundary Tests"
        },
        {
            "command": "python -m pytest tests/ -v --tb=short",
            "description": "All Tests (Summary)"
        },
        {
            "command": "python -m pytest tests/ --cov=. --cov-report=html --cov-report=term-missing",
            "description": "Coverage Report"
        }
    ]
    
    # Track results
    results = []
    
    # Run each test suite
    for test_config in test_commands:
        success = run_command(test_config["command"], test_config["description"])
        results.append({
            "description": test_config["description"],
            "success": success
        })
    
    # Print summary
    print(f"\n{'='*60}")
    print("TEST SUMMARY")
    print(f"{'='*60}")
    
    total_tests = len(results)
    passed_tests = sum(1 for r in results if r["success"])
    failed_tests = total_tests - passed_tests
    
    for result in results:
        status = "✅ PASSED" if result["success"] else "❌ FAILED"
        print(f"{status} - {result['description']}")
    
    print(f"\nTotal: {total_tests}, Passed: {passed_tests}, Failed: {failed_tests}")
    
    if failed_tests > 0:
        print(f"\n❌ {failed_tests} test suite(s) failed!")
        sys.exit(1)
    else:
        print(f"\n✅ All {passed_tests} test suites passed!")
        print("\nCoverage report generated in htmlcov/index.html")
        sys.exit(0)


if __name__ == "__main__":
    main()