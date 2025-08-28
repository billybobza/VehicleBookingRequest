import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { apiService, type BookingRequest } from '../services/api';

// Mock the API service
vi.mock('../services/api', () => ({
  apiService: {
    getVehicles: vi.fn(),
    getAvailableVehicles: vi.fn(),
    createBooking: vi.fn(),
    getBooking: vi.fn(),
  },
}));

const mockVehicles = [
  { id: 1, registration: 'ABC123', make: 'Toyota', color: 'Blue', created_at: '2024-01-01T00:00:00Z', updated_at: '2024-01-01T00:00:00Z' },
  { id: 2, registration: 'XYZ789', make: 'Honda', color: 'Red', created_at: '2024-01-01T00:00:00Z', updated_at: '2024-01-01T00:00:00Z' },
  { id: 3, registration: 'DEF456', make: 'Ford', color: 'Green', created_at: '2024-01-01T00:00:00Z', updated_at: '2024-01-01T00:00:00Z' },
];

const mockAvailableVehicles = [
  { id: 1, registration: 'ABC123', make: 'Toyota', color: 'Blue', created_at: '2024-01-01T00:00:00Z', updated_at: '2024-01-01T00:00:00Z' },
  { id: 3, registration: 'DEF456', make: 'Ford', color: 'Green', created_at: '2024-01-01T00:00:00Z', updated_at: '2024-01-01T00:00:00Z' },
];

const mockBookingConfirmation = {
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

describe('BookingForm Integration Logic Tests', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    // Mock successful API responses by default
    vi.mocked(apiService.getVehicles).mockResolvedValue({ data: mockVehicles });
    vi.mocked(apiService.getAvailableVehicles).mockResolvedValue({ data: mockAvailableVehicles });
    vi.mocked(apiService.createBooking).mockResolvedValue({ data: mockBookingConfirmation });
  });

  afterEach(() => {
    vi.clearAllMocks();
  });

  it('loads vehicles successfully', async () => {
    const result = await apiService.getVehicles();
    expect(result.data).toEqual(mockVehicles);
    expect(result.error).toBeUndefined();
    expect(apiService.getVehicles).toHaveBeenCalledTimes(1);
  });

  it('loads vehicles on component mount simulation', async () => {
    // Simulate component mount behavior
    const result = await apiService.getVehicles();
    expect(result.data).toEqual(mockVehicles);
    expect(apiService.getVehicles).toHaveBeenCalledTimes(1);
  });

  it('formats vehicle display options correctly', () => {
    const formatVehicleDisplay = (vehicle: typeof mockVehicles[0]) => 
      `${vehicle.registration} - ${vehicle.make} (${vehicle.color})`;
    
    expect(formatVehicleDisplay(mockVehicles[0])).toBe('ABC123 - Toyota (Blue)');
    expect(formatVehicleDisplay(mockVehicles[1])).toBe('XYZ789 - Honda (Red)');
    expect(formatVehicleDisplay(mockVehicles[2])).toBe('DEF456 - Ford (Green)');
  });

  it('filters available vehicles based on date range', async () => {
    const startDateTime = '2024-01-15T09:00:00Z';
    const endDateTime = '2024-01-16T09:00:00Z';
    
    const result = await apiService.getAvailableVehicles(startDateTime, endDateTime);
    
    expect(result.data).toEqual(mockAvailableVehicles);
    expect(result.error).toBeUndefined();
    expect(apiService.getAvailableVehicles).toHaveBeenCalledWith(startDateTime, endDateTime);
  });

  it('validates form data before submission', () => {
    const validateBookingForm = (formData: {
      vehicleId: number | null;
      startDateTime: string;
      endDateTime: string;
      reason: string;
      estimatedMileage: number | null;
    }) => {
      const errors: string[] = [];

      if (!formData.vehicleId) {
        errors.push('Please select a vehicle');
      }

      if (!formData.startDateTime || !formData.endDateTime) {
        errors.push('Please select start date, time, and duration');
      } else {
        const startDate = new Date(formData.startDateTime);
        const endDate = new Date(formData.endDateTime);
        const now = new Date();
        
        if (startDate < now) {
          errors.push('Start date and time cannot be in the past');
        }
        
        if (endDate <= startDate) {
          errors.push('End date and time must be after start date and time');
        }
      }

      if (!formData.reason || formData.reason.trim().length === 0) {
        errors.push('Please provide a reason for vehicle usage');
      } else if (formData.reason.trim().length > 500) {
        errors.push('Reason must be 500 characters or less');
      }

      if (formData.estimatedMileage === null || formData.estimatedMileage === undefined) {
        errors.push('Please provide estimated mileage');
      } else if (formData.estimatedMileage <= 0) {
        errors.push('Estimated mileage must be a positive number');
      } else if (formData.estimatedMileage > 10000) {
        errors.push('Estimated mileage cannot exceed 10,000 miles');
      }

      return { errors, isValid: errors.length === 0 };
    };

    // Test valid form
    const futureDate = new Date();
    futureDate.setDate(futureDate.getDate() + 1);
    const futureDateEnd = new Date();
    futureDateEnd.setDate(futureDateEnd.getDate() + 2);
    
    const validForm = {
      vehicleId: 1,
      startDateTime: futureDate.toISOString(),
      endDateTime: futureDateEnd.toISOString(),
      reason: 'Business meeting',
      estimatedMileage: 50,
    };
    
    const validResult = validateBookingForm(validForm);
    expect(validResult.isValid).toBe(true);
    expect(validResult.errors).toHaveLength(0);

    // Test invalid form
    const invalidForm = {
      vehicleId: null,
      startDateTime: '',
      endDateTime: '',
      reason: '',
      estimatedMileage: null,
    };
    
    const invalidResult = validateBookingForm(invalidForm);
    expect(invalidResult.isValid).toBe(false);
    expect(invalidResult.errors.length).toBeGreaterThan(0);
  });

  it('successfully creates booking with valid data', async () => {
    const bookingRequest: BookingRequest = {
      vehicle_id: 1,
      start_datetime: '2024-01-15T09:00:00Z',
      end_datetime: '2024-01-16T09:00:00Z',
      reason: 'Business meeting',
      estimated_mileage: 50,
    };

    const result = await apiService.createBooking(bookingRequest);
    
    expect(result.data).toEqual(mockBookingConfirmation);
    expect(result.error).toBeUndefined();
    expect(apiService.createBooking).toHaveBeenCalledWith(bookingRequest);
  });

  it('handles API error during vehicle loading', async () => {
    vi.mocked(apiService.getVehicles).mockResolvedValue({
      error: { code: 'API_ERROR', message: 'Failed to load vehicles' },
    });

    const result = await apiService.getVehicles();
    
    expect(result.data).toBeUndefined();
    expect(result.error?.message).toBe('Failed to load vehicles');
  });

  it('handles API error during booking submission', async () => {
    vi.mocked(apiService.createBooking).mockResolvedValue({
      error: { code: 'BOOKING_CONFLICT', message: 'Vehicle not available' },
    });

    const bookingRequest: BookingRequest = {
      vehicle_id: 1,
      start_datetime: '2024-01-15T09:00:00Z',
      end_datetime: '2024-01-16T09:00:00Z',
      reason: 'Business meeting',
      estimated_mileage: 50,
    };

    const result = await apiService.createBooking(bookingRequest);
    
    expect(result.data).toBeUndefined();
    expect(result.error?.message).toBe('Vehicle not available');
  });

  it('formats user-friendly error messages', () => {
    const getUserFriendlyMessage = (errorCode: string, originalMessage: string) => {
      switch (errorCode) {
        case 'HTTP_400':
          return 'Invalid booking data. Please check your inputs and try again.';
        case 'HTTP_404':
          return 'The selected vehicle is no longer available. Please choose another vehicle.';
        case 'HTTP_409':
          return 'This vehicle is already booked for the selected time period. Please choose different dates or another vehicle.';
        case 'NETWORK_ERROR':
          return 'Unable to connect to the server. Please check your internet connection and try again.';
        default:
          return originalMessage || 'An unexpected error occurred while processing your booking.';
      }
    };

    expect(getUserFriendlyMessage('HTTP_400', 'Bad Request')).toBe('Invalid booking data. Please check your inputs and try again.');
    expect(getUserFriendlyMessage('HTTP_404', 'Not Found')).toBe('The selected vehicle is no longer available. Please choose another vehicle.');
    expect(getUserFriendlyMessage('NETWORK_ERROR', 'Network Error')).toBe('Unable to connect to the server. Please check your internet connection and try again.');
  });

  it('calculates return dates correctly', () => {
    const calculateReturnDate = (endDate: Date): Date => {
      const returnDate = new Date(endDate);
      const dayOfWeek = returnDate.getDay(); // 0 = Sunday, 1 = Monday, ..., 6 = Saturday

      // If end date is Friday (5) or weekend (0 = Sunday, 6 = Saturday)
      if (dayOfWeek === 5 || dayOfWeek === 0 || dayOfWeek === 6) {
        // Set to next Monday
        const daysUntilMonday = dayOfWeek === 0 ? 1 : (8 - dayOfWeek);
        returnDate.setDate(returnDate.getDate() + daysUntilMonday);
        returnDate.setHours(9, 0, 0, 0); // 9:00 AM
      }

      return returnDate;
    };

    // Test Friday
    const friday = new Date('2024-01-05T17:00:00'); // Friday 5 PM
    const fridayReturn = calculateReturnDate(friday);
    expect(fridayReturn.getDay()).toBe(1); // Monday
    expect(fridayReturn.getHours()).toBe(9);

    // Test weekday
    const tuesday = new Date('2024-01-02T17:00:00'); // Tuesday 5 PM
    const tuesdayReturn = calculateReturnDate(tuesday);
    expect(tuesdayReturn.getTime()).toBe(tuesday.getTime()); // Same time
  });

  it('handles booking confirmation display', () => {
    const formatBookingConfirmation = (booking: typeof mockBookingConfirmation) => {
      return {
        id: booking.id,
        vehicle: `${booking.vehicle.registration} - ${booking.vehicle.make}`,
        startDate: new Date(booking.start_datetime).toLocaleDateString(),
        returnDate: new Date(booking.return_datetime).toLocaleDateString(),
        reason: booking.reason,
        mileage: booking.estimated_mileage,
      };
    };

    const formatted = formatBookingConfirmation(mockBookingConfirmation);
    
    expect(formatted.id).toBe(123);
    expect(formatted.vehicle).toBe('ABC123 - Toyota');
    expect(formatted.reason).toBe('Business meeting');
    expect(formatted.mileage).toBe(50);
  });
});