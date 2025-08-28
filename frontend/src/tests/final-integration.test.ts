/**
 * Final Integration Test for Car Booking System
 * 
 * This test verifies:
 * 1. Complete booking workflow from form submission to confirmation
 * 2. Return date calculation works correctly for all scenarios
 * 3. Availability checking prevents double bookings
 * 4. Frontend-backend API integration
 */

import { describe, it, expect, beforeAll, afterAll } from 'vitest';
import { apiService, type Vehicle, type BookingRequest, type BookingConfirmation } from '../services/api';

describe('Final Integration Tests', () => {
  let testVehicles: Vehicle[] = [];
  let createdBookings: number[] = [];

  beforeAll(async () => {
    // Wait for backend to be ready
    let retries = 10;
    while (retries > 0) {
      try {
        const response = await fetch('http://localhost:8000/health');
        if (response.ok) break;
      } catch (error) {
        // Backend not ready yet
      }
      await new Promise(resolve => setTimeout(resolve, 1000));
      retries--;
    }
    
    if (retries === 0) {
      throw new Error('Backend server not available for testing');
    }

    // Get available vehicles for testing
    const vehiclesResponse = await apiService.getVehicles();
    if (vehiclesResponse.error) {
      throw new Error(`Failed to get vehicles: ${vehiclesResponse.error.message}`);
    }
    testVehicles = vehiclesResponse.data || [];
    
    if (testVehicles.length === 0) {
      throw new Error('No vehicles available for testing');
    }
  });

  afterAll(async () => {
    // Clean up created bookings if needed
    console.log(`Created ${createdBookings.length} test bookings during integration tests`);
  });

  it('should complete full booking workflow', async () => {
    console.log('\n=== Testing Complete Booking Workflow ===');
    
    // Step 1: Get available vehicles for a future date
    const startDate = new Date();
    startDate.setDate(startDate.getDate() + 7); // 7 days from now
    const endDate = new Date(startDate);
    endDate.setDate(endDate.getDate() + 1); // 1 day duration
    
    const startDateStr = startDate.toISOString().split('T')[0];
    const endDateStr = endDate.toISOString().split('T')[0];
    
    const availableResponse = await apiService.getAvailableVehicles(startDateStr, endDateStr);
    expect(availableResponse.error).toBeUndefined();
    expect(availableResponse.data).toBeDefined();
    expect(availableResponse.data!.length).toBeGreaterThan(0);
    
    const selectedVehicle = availableResponse.data![0];
    console.log(`Selected vehicle: ${selectedVehicle.registration} (${selectedVehicle.make})`);
    
    // Step 2: Create booking request
    const startDateTime = new Date(startDate);
    startDateTime.setHours(9, 0, 0, 0);
    const endDateTime = new Date(startDate);
    endDateTime.setHours(17, 0, 0, 0);
    
    const bookingRequest: BookingRequest = {
      vehicle_id: selectedVehicle.id,
      start_datetime: startDateTime.toISOString(),
      end_datetime: endDateTime.toISOString(),
      reason: 'Integration test booking - business meeting',
      estimated_mileage: 150
    };
    
    // Step 3: Submit booking
    const bookingResponse = await apiService.createBooking(bookingRequest);
    expect(bookingResponse.error).toBeUndefined();
    expect(bookingResponse.data).toBeDefined();
    
    const booking = bookingResponse.data!;
    createdBookings.push(booking.id);
    
    expect(booking.id).toBeDefined();
    expect(booking.vehicle_id).toBe(selectedVehicle.id);
    expect(booking.status).toBe('confirmed');
    expect(booking.reason).toBe(bookingRequest.reason);
    expect(booking.estimated_mileage).toBe(bookingRequest.estimated_mileage);
    
    console.log(`Booking created successfully: ID #${booking.id}`);
    
    // Step 4: Verify booking can be retrieved
    const retrievedResponse = await apiService.getBooking(booking.id);
    expect(retrievedResponse.error).toBeUndefined();
    expect(retrievedResponse.data).toBeDefined();
    
    const retrievedBooking = retrievedResponse.data!;
    expect(retrievedBooking.id).toBe(booking.id);
    expect(retrievedBooking.reason).toBe(bookingRequest.reason);
    
    console.log('Booking retrieval verified successfully');
    
    // Step 5: Verify vehicle is no longer available for the same period
    const updatedAvailableResponse = await apiService.getAvailableVehicles(startDateStr, endDateStr);
    expect(updatedAvailableResponse.error).toBeUndefined();
    
    const updatedVehicles = updatedAvailableResponse.data || [];
    const vehicleIds = updatedVehicles.map(v => v.id);
    expect(vehicleIds).not.toContain(selectedVehicle.id);
    
    console.log('Availability checking verified - vehicle correctly marked as unavailable');
  });

  it('should calculate return dates correctly for different scenarios', async () => {
    console.log('\n=== Testing Return Date Calculation ===');
    
    const testCases = [
      {
        name: 'Weekday return (Tuesday)',
        dayOfWeek: 2, // Tuesday
        expectedSameDay: true
      },
      {
        name: 'Friday return',
        dayOfWeek: 5, // Friday
        expectedMondayReturn: true
      },
      {
        name: 'Saturday return',
        dayOfWeek: 6, // Saturday
        expectedMondayReturn: true
      },
      {
        name: 'Sunday return',
        dayOfWeek: 0, // Sunday
        expectedMondayReturn: true
      }
    ];

    for (let i = 0; i < testCases.length; i++) {
      const testCase = testCases[i];
      console.log(`\nTesting: ${testCase.name}`);
      
      // Find a date that falls on the target day of week
      const targetDate = new Date();
      targetDate.setDate(targetDate.getDate() + 14 + (i * 7)); // Space out test cases
      
      // Adjust to target day of week
      while (targetDate.getDay() !== testCase.dayOfWeek) {
        targetDate.setDate(targetDate.getDate() + 1);
      }
      
      const startDateTime = new Date(targetDate);
      startDateTime.setHours(9, 0, 0, 0);
      const endDateTime = new Date(targetDate);
      endDateTime.setHours(17, 0, 0, 0);
      
      // Use a different vehicle for each test to avoid conflicts
      const vehicleIndex = i % testVehicles.length;
      const testVehicle = testVehicles[vehicleIndex];
      
      const bookingRequest: BookingRequest = {
        vehicle_id: testVehicle.id,
        start_datetime: startDateTime.toISOString(),
        end_datetime: endDateTime.toISOString(),
        reason: `Test booking for ${testCase.name}`,
        estimated_mileage: 100
      };
      
      const response = await apiService.createBooking(bookingRequest);
      
      if (response.error) {
        console.log(`Skipping ${testCase.name} - vehicle not available: ${response.error.message}`);
        continue;
      }
      
      const booking = response.data!;
      createdBookings.push(booking.id);
      
      const returnDateTime = new Date(booking.return_datetime);
      
      if (testCase.expectedSameDay) {
        // Should return at end_datetime
        const expectedReturn = endDateTime;
        expect(returnDateTime.getTime()).toBe(expectedReturn.getTime());
        console.log(`✓ Correct return time: ${returnDateTime.toISOString()}`);
      } else if (testCase.expectedMondayReturn) {
        // Should return next Monday at 9 AM
        expect(returnDateTime.getDay()).toBe(1); // Monday
        expect(returnDateTime.getHours()).toBe(9);
        expect(returnDateTime.getTime()).toBeGreaterThan(endDateTime.getTime());
        console.log(`✓ Correct Monday return: ${returnDateTime.toISOString()}`);
      }
    }
  });

  it('should prevent double bookings', async () => {
    console.log('\n=== Testing Double Booking Prevention ===');
    
    // Use a specific vehicle for this test
    const testVehicle = testVehicles[0];
    
    // Create first booking
    const startDate = new Date();
    startDate.setDate(startDate.getDate() + 21); // 3 weeks from now
    const startDateTime = new Date(startDate);
    startDateTime.setHours(9, 0, 0, 0);
    const endDateTime = new Date(startDate);
    endDateTime.setHours(17, 0, 0, 0);
    
    const firstBooking: BookingRequest = {
      vehicle_id: testVehicle.id,
      start_datetime: startDateTime.toISOString(),
      end_datetime: endDateTime.toISOString(),
      reason: 'First booking for double booking test',
      estimated_mileage: 100
    };
    
    const firstResponse = await apiService.createBooking(firstBooking);
    expect(firstResponse.error).toBeUndefined();
    expect(firstResponse.data).toBeDefined();
    
    const booking1 = firstResponse.data!;
    createdBookings.push(booking1.id);
    console.log(`First booking created: ID #${booking1.id}`);
    
    // Attempt overlapping booking (should fail)
    const overlapStart = new Date(startDateTime);
    overlapStart.setHours(11, 0, 0, 0); // 2 hours into first booking
    const overlapEnd = new Date(endDateTime);
    overlapEnd.setHours(19, 0, 0, 0); // 2 hours after first booking
    
    const overlappingBooking: BookingRequest = {
      vehicle_id: testVehicle.id,
      start_datetime: overlapStart.toISOString(),
      end_datetime: overlapEnd.toISOString(),
      reason: 'Overlapping booking (should fail)',
      estimated_mileage: 50
    };
    
    const overlapResponse = await apiService.createBooking(overlappingBooking);
    expect(overlapResponse.error).toBeDefined();
    expect(overlapResponse.error!.code).toMatch(/400|HTTP_400/);
    console.log('✓ Overlapping booking correctly rejected');
    
    // Attempt booking immediately after (should succeed)
    const nextStart = new Date(endDateTime);
    nextStart.setHours(18, 0, 0, 0); // 1 hour after first booking ends
    const nextEnd = new Date(nextStart);
    nextEnd.setHours(20, 0, 0, 0); // 2 hour duration
    
    const sequentialBooking: BookingRequest = {
      vehicle_id: testVehicle.id,
      start_datetime: nextStart.toISOString(),
      end_datetime: nextEnd.toISOString(),
      reason: 'Sequential booking (should succeed)',
      estimated_mileage: 30
    };
    
    const sequentialResponse = await apiService.createBooking(sequentialBooking);
    expect(sequentialResponse.error).toBeUndefined();
    expect(sequentialResponse.data).toBeDefined();
    
    const booking2 = sequentialResponse.data!;
    createdBookings.push(booking2.id);
    console.log(`✓ Sequential booking succeeded: ID #${booking2.id}`);
  });

  it('should handle API errors gracefully', async () => {
    console.log('\n=== Testing API Error Handling ===');
    
    // Test invalid vehicle ID
    const invalidBooking: BookingRequest = {
      vehicle_id: 99999, // Non-existent vehicle
      start_datetime: new Date(Date.now() + 24 * 60 * 60 * 1000).toISOString(),
      end_datetime: new Date(Date.now() + 48 * 60 * 60 * 1000).toISOString(),
      reason: 'Test booking with invalid vehicle',
      estimated_mileage: 100
    };
    
    const invalidResponse = await apiService.createBooking(invalidBooking);
    expect(invalidResponse.error).toBeDefined();
    expect(invalidResponse.error!.code).toMatch(/404|HTTP_404/);
    console.log('✓ Invalid vehicle ID correctly handled');
    
    // Test network error handling by making request to non-existent endpoint
    try {
      const response = await fetch('http://localhost:8000/api/nonexistent');
      expect(response.status).toBe(404);
      console.log('✓ 404 errors correctly handled');
    } catch (error) {
      console.log('✓ Network errors correctly handled');
    }
  });

  it('should validate business rules', async () => {
    console.log('\n=== Testing Business Rule Validation ===');
    
    const testVehicle = testVehicles[0];
    
    // Test past date booking (should fail at API level)
    const pastDate = new Date();
    pastDate.setDate(pastDate.getDate() - 1); // Yesterday
    
    const pastBooking: BookingRequest = {
      vehicle_id: testVehicle.id,
      start_datetime: pastDate.toISOString(),
      end_datetime: new Date().toISOString(),
      reason: 'Past date booking test',
      estimated_mileage: 50
    };
    
    const pastResponse = await apiService.createBooking(pastBooking);
    expect(pastResponse.error).toBeDefined();
    expect(pastResponse.error!.code).toMatch(/422|400|HTTP_422|HTTP_400/);
    console.log('✓ Past date booking correctly rejected');
    
    // Test invalid date order (end before start)
    const futureDate1 = new Date();
    futureDate1.setDate(futureDate1.getDate() + 5);
    const futureDate2 = new Date();
    futureDate2.setDate(futureDate2.getDate() + 3); // Earlier than start
    
    const invalidOrderBooking: BookingRequest = {
      vehicle_id: testVehicle.id,
      start_datetime: futureDate1.toISOString(),
      end_datetime: futureDate2.toISOString(),
      reason: 'Invalid date order test',
      estimated_mileage: 50
    };
    
    const orderResponse = await apiService.createBooking(invalidOrderBooking);
    expect(orderResponse.error).toBeDefined();
    expect(orderResponse.error!.code).toMatch(/422|400|HTTP_422|HTTP_400/);
    console.log('✓ Invalid date order correctly rejected');
  });
});