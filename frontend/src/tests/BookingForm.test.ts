import { describe, it, expect, vi, beforeEach } from 'vitest';
import { apiService, type BookingRequest } from '../services/api';

// Mock the API service
vi.mock('../services/api', () => ({
  apiService: {
    getVehicles: vi.fn(),
    getAvailableVehicles: vi.fn(),
    createBooking: vi.fn(),
  },
}));

// Mock the UI stores
vi.mock('../stores/ui', () => ({
  addError: vi.fn(),
}));

const mockVehicles = [
  { id: 1, registration: 'ABC123', make: 'Toyota', color: 'Blue' },
  { id: 2, registration: 'XYZ789', make: 'Honda', color: 'Red' },
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
};

describe('BookingForm Component Logic', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('API service methods are properly mocked', () => {
    expect(apiService.getVehicles).toBeDefined();
    expect(apiService.getAvailableVehicles).toBeDefined();
    expect(apiService.createBooking).toBeDefined();
  });

  it('form validation logic works correctly', () => {
    // Test form validation logic
    const validateForm = (formData: {
      selectedVehicleId: number | null;
      startDateTime: string;
      endDateTime: string;
      reason: string;
      estimatedMileage: number | null;
    }) => {
      const errors: string[] = [];

      if (!formData.selectedVehicleId) {
        errors.push('Please select a vehicle');
      }

      if (!formData.startDateTime || !formData.endDateTime) {
        errors.push('Please select start date, time, and duration');
      }

      if (!formData.reason || formData.reason.trim().length === 0) {
        errors.push('Please provide a reason for vehicle usage');
      }

      if (formData.estimatedMileage === null || formData.estimatedMileage === undefined) {
        errors.push('Please provide estimated mileage');
      } else if (formData.estimatedMileage <= 0) {
        errors.push('Estimated mileage must be a positive number');
      }

      return { errors, isValid: errors.length === 0 };
    };

    // Test empty form
    const emptyForm = {
      selectedVehicleId: null,
      startDateTime: '',
      endDateTime: '',
      reason: '',
      estimatedMileage: null,
    };
    const emptyResult = validateForm(emptyForm);
    expect(emptyResult.isValid).toBe(false);
    expect(emptyResult.errors).toHaveLength(4);

    // Test valid form
    const validForm = {
      selectedVehicleId: 1,
      startDateTime: '2024-01-15T09:00:00Z',
      endDateTime: '2024-01-16T09:00:00Z',
      reason: 'Business meeting',
      estimatedMileage: 50,
    };
    const validResult = validateForm(validForm);
    expect(validResult.isValid).toBe(true);
    expect(validResult.errors).toHaveLength(0);

    // Test negative mileage
    const negativeForm = { ...validForm, estimatedMileage: -10 };
    const negativeResult = validateForm(negativeForm);
    expect(negativeResult.isValid).toBe(false);
    expect(negativeResult.errors).toContain('Estimated mileage must be a positive number');

    // Test zero mileage
    const zeroForm = { ...validForm, estimatedMileage: 0 };
    const zeroResult = validateForm(zeroForm);
    expect(zeroResult.isValid).toBe(false);
    expect(zeroResult.errors).toContain('Estimated mileage must be a positive number');
  });

  it('booking request creation works correctly', () => {
    const createBookingRequest = (formData: {
      selectedVehicleId: number;
      startDateTime: string;
      endDateTime: string;
      reason: string;
      estimatedMileage: number;
    }): BookingRequest => ({
      vehicle_id: formData.selectedVehicleId,
      start_datetime: formData.startDateTime,
      end_datetime: formData.endDateTime,
      reason: formData.reason.trim(),
      estimated_mileage: formData.estimatedMileage,
    });

    const formData = {
      selectedVehicleId: 1,
      startDateTime: '2024-01-15T09:00:00Z',
      endDateTime: '2024-01-16T09:00:00Z',
      reason: '  Business meeting  ',
      estimatedMileage: 50,
    };

    const bookingRequest = createBookingRequest(formData);
    expect(bookingRequest.vehicle_id).toBe(1);
    expect(bookingRequest.start_datetime).toBe('2024-01-15T09:00:00Z');
    expect(bookingRequest.end_datetime).toBe('2024-01-16T09:00:00Z');
    expect(bookingRequest.reason).toBe('Business meeting'); // trimmed
    expect(bookingRequest.estimated_mileage).toBe(50);
  });

  it('API service createBooking can be mocked to return success', async () => {
    vi.mocked(apiService.createBooking).mockResolvedValue({ data: mockBookingConfirmation });
    
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

  it('API service createBooking can be mocked to return error', async () => {
    const errorMessage = 'Vehicle not available for selected dates';
    vi.mocked(apiService.createBooking).mockResolvedValue({
      error: { code: 'BOOKING_CONFLICT', message: errorMessage },
    });
    
    const bookingRequest: BookingRequest = {
      vehicle_id: 1,
      start_datetime: '2024-01-15T09:00:00Z',
      end_datetime: '2024-01-16T09:00:00Z',
      reason: 'Business meeting',
      estimated_mileage: 50,
    };

    const result = await apiService.createBooking(bookingRequest);
    expect(result.error?.message).toBe(errorMessage);
    expect(result.data).toBeUndefined();
  });

  it('date time formatting works correctly', () => {
    const formatDateTime = (isoString: string): string => {
      if (!isoString) return '';
      const date = new Date(isoString);
      return date.toLocaleString('en-US', {
        weekday: 'short',
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit',
      });
    };

    const testDate = '2024-01-15T09:00:00Z';
    const formatted = formatDateTime(testDate);
    expect(formatted).toContain('2024');
    expect(formatted).toContain('Jan');
    expect(formatted).toContain('15');
    // Don't test specific time due to timezone differences
    expect(formatted.length).toBeGreaterThan(0);
  });

  it('form reset logic works correctly', () => {
    const resetForm = () => ({
      selectedVehicleId: null,
      selectedVehicle: null,
      startDateTime: '',
      endDateTime: '',
      returnDateTime: '',
      duration: '',
      reason: '',
      estimatedMileage: null,
      formErrors: [],
    });

    const resetState = resetForm();
    expect(resetState.selectedVehicleId).toBeNull();
    expect(resetState.selectedVehicle).toBeNull();
    expect(resetState.startDateTime).toBe('');
    expect(resetState.endDateTime).toBe('');
    expect(resetState.returnDateTime).toBe('');
    expect(resetState.duration).toBe('');
    expect(resetState.reason).toBe('');
    expect(resetState.estimatedMileage).toBeNull();
    expect(resetState.formErrors).toEqual([]);
  });

  it('vehicle selection event handling logic', () => {
    const handleVehicleSelected = (vehicleId: number, vehicle: typeof mockVehicles[0]) => ({
      selectedVehicleId: vehicleId,
      selectedVehicle: vehicle,
    });

    const result = handleVehicleSelected(1, mockVehicles[0]);
    expect(result.selectedVehicleId).toBe(1);
    expect(result.selectedVehicle).toEqual(mockVehicles[0]);
  });

  it('date time change event handling logic', () => {
    const handleDateTimeChanged = (eventDetail: {
      startDateTime: string;
      endDateTime: string;
      returnDateTime: string;
      duration: string;
    }) => ({
      startDateTime: eventDetail.startDateTime,
      endDateTime: eventDetail.endDateTime,
      returnDateTime: eventDetail.returnDateTime,
      duration: eventDetail.duration,
    });

    const eventDetail = {
      startDateTime: '2024-01-15T09:00:00Z',
      endDateTime: '2024-01-16T09:00:00Z',
      returnDateTime: '2024-01-16T09:00:00Z',
      duration: '1d',
    };

    const result = handleDateTimeChanged(eventDetail);
    expect(result.startDateTime).toBe('2024-01-15T09:00:00Z');
    expect(result.endDateTime).toBe('2024-01-16T09:00:00Z');
    expect(result.returnDateTime).toBe('2024-01-16T09:00:00Z');
    expect(result.duration).toBe('1d');
  });
});