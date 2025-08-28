import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { apiService, type Vehicle, type BookingRequest, type BookingConfirmation } from '../services/api';

// Mock fetch for E2E-style testing
global.fetch = vi.fn();

const mockVehicles: Vehicle[] = [
  { id: 1, registration: 'ABC123', make: 'Toyota', color: 'Blue', created_at: '2024-01-01T00:00:00Z', updated_at: '2024-01-01T00:00:00Z' },
  { id: 2, registration: 'XYZ789', make: 'Honda', color: 'Red', created_at: '2024-01-01T00:00:00Z', updated_at: '2024-01-01T00:00:00Z' },
  { id: 3, registration: 'DEF456', make: 'Ford', color: 'Green', created_at: '2024-01-01T00:00:00Z', updated_at: '2024-01-01T00:00:00Z' },
];

const mockAvailableVehicles: Vehicle[] = [
  { id: 1, registration: 'ABC123', make: 'Toyota', color: 'Blue', created_at: '2024-01-01T00:00:00Z', updated_at: '2024-01-01T00:00:00Z' },
  { id: 3, registration: 'DEF456', make: 'Ford', color: 'Green', created_at: '2024-01-01T00:00:00Z', updated_at: '2024-01-01T00:00:00Z' },
];

const mockBookingConfirmation: BookingConfirmation = {
  id: 123,
  vehicle_id: 1,
  start_datetime: '2024-01-15T09:00:00Z',
  end_datetime: '2024-01-16T09:00:00Z',
  return_datetime: '2024-01-16T09:00:00Z',
  reason: 'Business meeting',
  estimated_mileage: 50,
  status: 'confirmed',
  created_at: '2024-01-14T10:00:00Z',
  vehicle: { id: 1, registration: 'ABC123', make: 'Toyota', color: 'Blue', created_at: '2024-01-01T00:00:00Z', updated_at: '2024-01-01T00:00:00Z' },
};

describe('End-to-End Booking Workflow Tests', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  afterEach(() => {
    vi.clearAllMocks();
  });

  it('completes successful booking workflow', async () => {
    // Mock API responses for successful workflow
    vi.mocked(fetch)
      .mockResolvedValueOnce({
        ok: true,
        json: async () => mockVehicles,
      } as Response)
      .mockResolvedValueOnce({
        ok: true,
        json: async () => mockAvailableVehicles,
      } as Response)
      .mockResolvedValueOnce({
        ok: true,
        status: 201,
        json: async () => mockBookingConfirmation,
      } as Response)
      .mockResolvedValueOnce({
        ok: true,
        json: async () => mockBookingConfirmation,
      } as Response);

    // Step 1: Load all vehicles
    const vehiclesResult = await apiService.getVehicles();
    expect(vehiclesResult.data).toEqual(mockVehicles);
    expect(vehiclesResult.error).toBeUndefined();

    // Step 2: Check available vehicles for specific date range
    const startDateTime = '2024-01-15T09:00:00Z';
    const endDateTime = '2024-01-16T09:00:00Z';
    
    const availableResult = await apiService.getAvailableVehicles(startDateTime, endDateTime);
    expect(availableResult.data).toEqual(mockAvailableVehicles);
    expect(availableResult.error).toBeUndefined();

    // Step 3: Create booking for available vehicle
    const bookingRequest: BookingRequest = {
      vehicle_id: 1,
      start_datetime: startDateTime,
      end_datetime: endDateTime,
      reason: 'Business meeting',
      estimated_mileage: 50,
    };

    const bookingResult = await apiService.createBooking(bookingRequest);
    expect(bookingResult.data).toEqual(mockBookingConfirmation);
    expect(bookingResult.error).toBeUndefined();

    // Step 4: Retrieve created booking
    const retrieveResult = await apiService.getBooking(123);
    expect(retrieveResult.data).toEqual(mockBookingConfirmation);
    expect(retrieveResult.error).toBeUndefined();

    // Verify API calls were made correctly
    expect(fetch).toHaveBeenCalledTimes(4);
    expect(fetch).toHaveBeenNthCalledWith(1, 'http://localhost:8000/api/vehicles/', expect.any(Object));
    expect(fetch).toHaveBeenNthCalledWith(2, expect.stringContaining('/api/vehicles/available'), expect.any(Object));
    expect(fetch).toHaveBeenNthCalledWith(3, 'http://localhost:8000/api/bookings/', expect.objectContaining({
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(bookingRequest),
    }));
    expect(fetch).toHaveBeenNthCalledWith(4, 'http://localhost:8000/api/bookings/123', expect.any(Object));
  });

  it('handles vehicle unavailability during booking workflow', async () => {
    // Mock API responses where vehicle becomes unavailable
    vi.mocked(fetch)
      .mockResolvedValueOnce({
        ok: true,
        json: async () => mockVehicles,
      } as Response)
      .mockResolvedValueOnce({
        ok: true,
        json: async () => mockAvailableVehicles,
      } as Response)
      .mockResolvedValueOnce({
        ok: false,
        status: 400,
        json: async () => ({
          error: {
            code: 'BOOKING_CONFLICT',
            message: 'Vehicle is not available for the requested time period'
          }
        }),
      } as Response);

    // Step 1: Load vehicles
    const vehiclesResult = await apiService.getVehicles();
    expect(vehiclesResult.data).toEqual(mockVehicles);

    // Step 2: Check availability
    const availableResult = await apiService.getAvailableVehicles('2024-01-15T09:00:00Z', '2024-01-16T09:00:00Z');
    expect(availableResult.data).toEqual(mockAvailableVehicles);

    // Step 3: Attempt booking (fails due to conflict)
    const bookingRequest: BookingRequest = {
      vehicle_id: 1,
      start_datetime: '2024-01-15T09:00:00Z',
      end_datetime: '2024-01-16T09:00:00Z',
      reason: 'Business meeting',
      estimated_mileage: 50,
    };

    const bookingResult = await apiService.createBooking(bookingRequest);
    expect(bookingResult.data).toBeUndefined();
    expect(bookingResult.error).toEqual({
      code: 'HTTP_400',
      message: 'Vehicle is not available for the requested time period',
      details: undefined
    });
  });

  it('handles network errors during booking workflow', async () => {
    // Mock network error
    vi.mocked(fetch).mockRejectedValueOnce(new Error('Network error'));

    const vehiclesResult = await apiService.getVehicles();
    expect(vehiclesResult.data).toBeUndefined();
    expect(vehiclesResult.error).toEqual({
      code: 'NETWORK_ERROR',
      message: 'Network error'
    });
  });

  it('handles validation errors during booking creation', async () => {
    // Mock validation error response
    vi.mocked(fetch).mockResolvedValueOnce({
      ok: false,
      status: 422,
      json: async () => ({
        error: {
          code: 'VALIDATION_ERROR',
          message: 'Validation failed',
          details: [
            { loc: ['body', 'estimated_mileage'], msg: 'must be positive', type: 'value_error' },
            { loc: ['body', 'reason'], msg: 'cannot be empty', type: 'value_error' }
          ]
        }
      }),
    } as Response);

    const bookingRequest: BookingRequest = {
      vehicle_id: 1,
      start_datetime: '2024-01-15T09:00:00Z',
      end_datetime: '2024-01-16T09:00:00Z',
      reason: '',
      estimated_mileage: -10,
    };

    const bookingResult = await apiService.createBooking(bookingRequest);
    expect(bookingResult.data).toBeUndefined();
    expect(bookingResult.error).toEqual({
      code: 'HTTP_422',
      message: 'Validation failed',
      details: [
        { loc: ['body', 'estimated_mileage'], msg: 'must be positive', type: 'value_error' },
        { loc: ['body', 'reason'], msg: 'cannot be empty', type: 'value_error' }
      ]
    });
  });

  it('handles server errors during booking workflow', async () => {
    // Mock server error
    vi.mocked(fetch).mockResolvedValueOnce({
      ok: false,
      status: 500,
      statusText: 'Internal Server Error',
      json: async () => ({
        error: {
          code: 'INTERNAL_SERVER_ERROR',
          message: 'An internal server error occurred'
        }
      }),
    } as Response);

    const vehiclesResult = await apiService.getVehicles();
    expect(vehiclesResult.data).toBeUndefined();
    expect(vehiclesResult.error).toEqual({
      code: 'HTTP_500',
      message: 'An internal server error occurred',
      details: undefined
    });
  });

  it('completes booking workflow with Friday return date calculation', async () => {
    // Mock booking that ends on Friday
    const fridayBookingConfirmation: BookingConfirmation = {
      ...mockBookingConfirmation,
      end_datetime: '2024-01-05T17:00:00Z', // Friday 5 PM
      return_datetime: '2024-01-08T09:00:00Z', // Monday 9 AM
    };

    vi.mocked(fetch)
      .mockResolvedValueOnce({
        ok: true,
        json: async () => mockVehicles,
      } as Response)
      .mockResolvedValueOnce({
        ok: true,
        json: async () => mockAvailableVehicles,
      } as Response)
      .mockResolvedValueOnce({
        ok: true,
        status: 201,
        json: async () => fridayBookingConfirmation,
      } as Response);

    // Complete workflow
    await apiService.getVehicles();
    await apiService.getAvailableVehicles('2024-01-05T09:00:00Z', '2024-01-05T17:00:00Z');

    const bookingRequest: BookingRequest = {
      vehicle_id: 1,
      start_datetime: '2024-01-05T09:00:00Z',
      end_datetime: '2024-01-05T17:00:00Z',
      reason: 'Friday meeting',
      estimated_mileage: 25,
    };

    const bookingResult = await apiService.createBooking(bookingRequest);
    expect(bookingResult.data?.return_datetime).toBe('2024-01-08T09:00:00Z');
  });

  it('completes booking workflow with weekend return date calculation', async () => {
    // Mock booking that ends on Sunday
    const sundayBookingConfirmation: BookingConfirmation = {
      ...mockBookingConfirmation,
      end_datetime: '2024-01-07T15:00:00Z', // Sunday 3 PM
      return_datetime: '2024-01-08T09:00:00Z', // Monday 9 AM
    };

    vi.mocked(fetch)
      .mockResolvedValueOnce({
        ok: true,
        json: async () => mockVehicles,
      } as Response)
      .mockResolvedValueOnce({
        ok: true,
        json: async () => mockAvailableVehicles,
      } as Response)
      .mockResolvedValueOnce({
        ok: true,
        status: 201,
        json: async () => sundayBookingConfirmation,
      } as Response);

    // Complete workflow
    await apiService.getVehicles();
    await apiService.getAvailableVehicles('2024-01-07T09:00:00Z', '2024-01-07T15:00:00Z');

    const bookingRequest: BookingRequest = {
      vehicle_id: 1,
      start_datetime: '2024-01-07T09:00:00Z',
      end_datetime: '2024-01-07T15:00:00Z',
      reason: 'Sunday event',
      estimated_mileage: 30,
    };

    const bookingResult = await apiService.createBooking(bookingRequest);
    expect(bookingResult.data?.return_datetime).toBe('2024-01-08T09:00:00Z');
  });

  it('handles concurrent booking attempts', async () => {
    // Mock successful first booking, then conflict for second
    vi.mocked(fetch)
      .mockResolvedValueOnce({
        ok: true,
        json: async () => mockVehicles,
      } as Response)
      .mockResolvedValueOnce({
        ok: true,
        json: async () => mockAvailableVehicles,
      } as Response)
      .mockResolvedValueOnce({
        ok: true,
        status: 201,
        json: async () => mockBookingConfirmation,
      } as Response)
      .mockResolvedValueOnce({
        ok: true,
        json: async () => [mockAvailableVehicles[1]], // Only second vehicle available now
      } as Response)
      .mockResolvedValueOnce({
        ok: false,
        status: 400,
        json: async () => ({
          error: {
            code: 'BOOKING_CONFLICT',
            message: 'Vehicle is not available for the requested time period'
          }
        }),
      } as Response);

    const bookingRequest: BookingRequest = {
      vehicle_id: 1,
      start_datetime: '2024-01-15T09:00:00Z',
      end_datetime: '2024-01-16T09:00:00Z',
      reason: 'First booking',
      estimated_mileage: 50,
    };

    // First booking succeeds
    await apiService.getVehicles();
    await apiService.getAvailableVehicles('2024-01-15T09:00:00Z', '2024-01-16T09:00:00Z');
    const firstBooking = await apiService.createBooking(bookingRequest);
    expect(firstBooking.data).toEqual(mockBookingConfirmation);

    // Check availability again (vehicle 1 no longer available)
    const updatedAvailable = await apiService.getAvailableVehicles('2024-01-15T09:00:00Z', '2024-01-16T09:00:00Z');
    expect(updatedAvailable.data).toHaveLength(1);

    // Second booking for same vehicle fails
    const secondBookingRequest: BookingRequest = {
      ...bookingRequest,
      reason: 'Second booking attempt',
    };

    const secondBooking = await apiService.createBooking(secondBookingRequest);
    expect(secondBooking.data).toBeUndefined();
    expect(secondBooking.error?.code).toBe('HTTP_400');
  });

  it('handles booking retrieval after creation', async () => {
    // Mock successful booking creation and retrieval
    vi.mocked(fetch)
      .mockResolvedValueOnce({
        ok: true,
        status: 201,
        json: async () => mockBookingConfirmation,
      } as Response)
      .mockResolvedValueOnce({
        ok: true,
        json: async () => mockBookingConfirmation,
      } as Response);

    const bookingRequest: BookingRequest = {
      vehicle_id: 1,
      start_datetime: '2024-01-15T09:00:00Z',
      end_datetime: '2024-01-16T09:00:00Z',
      reason: 'Business meeting',
      estimated_mileage: 50,
    };

    // Create booking
    const createResult = await apiService.createBooking(bookingRequest);
    expect(createResult.data?.id).toBe(123);

    // Retrieve booking
    const retrieveResult = await apiService.getBooking(123);
    expect(retrieveResult.data).toEqual(mockBookingConfirmation);
    expect(retrieveResult.data?.vehicle.registration).toBe('ABC123');
  });

  it('handles booking retrieval for non-existent booking', async () => {
    // Mock 404 response
    vi.mocked(fetch).mockResolvedValueOnce({
      ok: false,
      status: 404,
      json: async () => ({
        error: {
          code: 'NOT_FOUND',
          message: 'Booking with ID 999 not found'
        }
      }),
    } as Response);

    const retrieveResult = await apiService.getBooking(999);
    expect(retrieveResult.data).toBeUndefined();
    expect(retrieveResult.error).toEqual({
      code: 'HTTP_404',
      message: 'Booking with ID 999 not found',
      details: undefined
    });
  });

  it('handles complex availability filtering workflow', async () => {
    // Mock scenario with multiple vehicles and complex availability
    const complexAvailableVehicles = [mockVehicles[2]]; // Only Ford available

    vi.mocked(fetch)
      .mockResolvedValueOnce({
        ok: true,
        json: async () => mockVehicles,
      } as Response)
      .mockResolvedValueOnce({
        ok: true,
        json: async () => complexAvailableVehicles,
      } as Response)
      .mockResolvedValueOnce({
        ok: true,
        status: 201,
        json: async () => ({
          ...mockBookingConfirmation,
          vehicle_id: 3,
          vehicle: mockVehicles[2],
        }),
      } as Response);

    // Get all vehicles
    const allVehicles = await apiService.getVehicles();
    expect(allVehicles.data).toHaveLength(3);

    // Check availability for specific period
    const availableVehicles = await apiService.getAvailableVehicles('2024-01-20T09:00:00Z', '2024-01-22T17:00:00Z');
    expect(availableVehicles.data).toHaveLength(1);
    expect(availableVehicles.data?.[0].registration).toBe('DEF456');

    // Book the available vehicle
    const bookingRequest: BookingRequest = {
      vehicle_id: 3,
      start_datetime: '2024-01-20T09:00:00Z',
      end_datetime: '2024-01-22T17:00:00Z',
      reason: 'Long trip',
      estimated_mileage: 500,
    };

    const bookingResult = await apiService.createBooking(bookingRequest);
    expect(bookingResult.data?.vehicle_id).toBe(3);
    expect(bookingResult.data?.vehicle.registration).toBe('DEF456');
  });
});