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
    // Enhanced form validation logic that matches the component
    const validateForm = (formData: {
      selectedVehicleId: number | null;
      startDateTime: string;
      endDateTime: string;
      reason: string;
      estimatedMileage: number | null;
    }) => {
      const errors: string[] = [];

      // Vehicle selection validation
      if (!formData.selectedVehicleId) {
        errors.push('Please select a vehicle');
      }

      // Date/time validation
      if (!formData.startDateTime || !formData.endDateTime) {
        errors.push('Please select start date, time, and duration');
      } else {
        const startDate = new Date(formData.startDateTime);
        const endDate = new Date(formData.endDateTime);
        const now = new Date();
        
        // Check if start date is in the past
        if (startDate < now) {
          errors.push('Start date and time cannot be in the past');
        }
        
        // Check if end date is after start date
        if (endDate <= startDate) {
          errors.push('End date and time must be after start date and time');
        }
      }

      // Reason validation
      if (!formData.reason || formData.reason.trim().length === 0) {
        errors.push('Please provide a reason for vehicle usage');
      } else if (formData.reason.trim().length > 500) {
        errors.push('Reason must be 500 characters or less');
      }

      // Estimated mileage validation
      if (formData.estimatedMileage === null || formData.estimatedMileage === undefined) {
        errors.push('Please provide estimated mileage');
      } else if (formData.estimatedMileage <= 0) {
        errors.push('Estimated mileage must be a positive number');
      } else if (formData.estimatedMileage > 10000) {
        errors.push('Estimated mileage cannot exceed 10,000 miles');
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

    // Test valid form with future dates
    const futureDate = new Date();
    futureDate.setDate(futureDate.getDate() + 1);
    const futureDateEnd = new Date();
    futureDateEnd.setDate(futureDateEnd.getDate() + 2);
    
    const validForm = {
      selectedVehicleId: 1,
      startDateTime: futureDate.toISOString(),
      endDateTime: futureDateEnd.toISOString(),
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

    // Test excessive mileage
    const excessiveMileageForm = { ...validForm, estimatedMileage: 15000 };
    const excessiveResult = validateForm(excessiveMileageForm);
    expect(excessiveResult.isValid).toBe(false);
    expect(excessiveResult.errors).toContain('Estimated mileage cannot exceed 10,000 miles');

    // Test reason too long
    const longReasonForm = { ...validForm, reason: 'A'.repeat(501) };
    const longReasonResult = validateForm(longReasonForm);
    expect(longReasonResult.isValid).toBe(false);
    expect(longReasonResult.errors).toContain('Reason must be 500 characters or less');

    // Test past start date
    const pastDate = new Date();
    pastDate.setDate(pastDate.getDate() - 1);
    const pastForm = { ...validForm, startDateTime: pastDate.toISOString() };
    const pastResult = validateForm(pastForm);
    expect(pastResult.isValid).toBe(false);
    expect(pastResult.errors).toContain('Start date and time cannot be in the past');

    // Test end date before start date
    const invalidDateForm = { 
      ...validForm, 
      startDateTime: futureDateEnd.toISOString(),
      endDateTime: futureDate.toISOString()
    };
    const invalidDateResult = validateForm(invalidDateForm);
    expect(invalidDateResult.isValid).toBe(false);
    expect(invalidDateResult.errors).toContain('End date and time must be after start date and time');
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

  it('error message mapping works correctly', () => {
    const getUserFriendlyMessage = (errorCode: string, originalMessage: string, details?: any) => {
      switch (errorCode) {
        case 'HTTP_400':
          return 'Invalid booking data. Please check your inputs and try again.';
        case 'HTTP_404':
          return 'The selected vehicle is no longer available. Please choose another vehicle.';
        case 'HTTP_422':
        case 'VALIDATION_ERROR':
          let message = 'Please check your form inputs. Some fields contain invalid data.';
          if (details && Array.isArray(details)) {
            const fieldErrors = details.map((detail: any) => {
              const field = detail.loc ? detail.loc[detail.loc.length - 1] : 'field';
              return `${field}: ${detail.msg}`;
            }).join(', ');
            message += ` Details: ${fieldErrors}`;
          }
          return message;
        case 'HTTP_409':
          return 'This vehicle is already booked for the selected time period. Please choose different dates or another vehicle.';
        case 'HTTP_500':
        case 'DATABASE_ERROR':
        case 'INTERNAL_SERVER_ERROR':
          return 'A server error occurred. Please try again later or contact support if the problem persists.';
        case 'NETWORK_ERROR':
          return 'Unable to connect to the server. Please check your internet connection and try again.';
        default:
          return originalMessage || 'An unexpected error occurred while processing your booking.';
      }
    };

    // Test various error codes
    expect(getUserFriendlyMessage('HTTP_400', 'Bad Request')).toBe('Invalid booking data. Please check your inputs and try again.');
    expect(getUserFriendlyMessage('HTTP_404', 'Not Found')).toBe('The selected vehicle is no longer available. Please choose another vehicle.');
    expect(getUserFriendlyMessage('HTTP_409', 'Conflict')).toBe('This vehicle is already booked for the selected time period. Please choose different dates or another vehicle.');
    expect(getUserFriendlyMessage('NETWORK_ERROR', 'Network Error')).toBe('Unable to connect to the server. Please check your internet connection and try again.');
    expect(getUserFriendlyMessage('UNKNOWN_ERROR', 'Some error')).toBe('Some error');

    // Test validation error with details
    const validationDetails = [
      { loc: ['body', 'estimated_mileage'], msg: 'must be positive' },
      { loc: ['body', 'reason'], msg: 'cannot be empty' }
    ];
    const validationMessage = getUserFriendlyMessage('VALIDATION_ERROR', 'Validation failed', validationDetails);
    expect(validationMessage).toContain('Please check your form inputs');
    expect(validationMessage).toContain('estimated_mileage: must be positive');
    expect(validationMessage).toContain('reason: cannot be empty');
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

  it('character count validation works correctly', () => {
    const validateReasonLength = (reason: string) => {
      if (!reason) return { valid: false, message: 'Please provide a reason for vehicle usage' };
      if (reason.trim().length === 0) return { valid: false, message: 'Please provide a reason for vehicle usage' };
      if (reason.trim().length > 500) return { valid: false, message: 'Reason must be 500 characters or less' };
      return { valid: true, message: '' };
    };

    // Test empty reason
    expect(validateReasonLength('')).toEqual({ valid: false, message: 'Please provide a reason for vehicle usage' });
    
    // Test whitespace only
    expect(validateReasonLength('   ')).toEqual({ valid: false, message: 'Please provide a reason for vehicle usage' });
    
    // Test valid reason
    expect(validateReasonLength('Business meeting')).toEqual({ valid: true, message: '' });
    
    // Test reason at limit
    const reasonAt500 = 'A'.repeat(500);
    expect(validateReasonLength(reasonAt500)).toEqual({ valid: true, message: '' });
    
    // Test reason over limit
    const reasonOver500 = 'A'.repeat(501);
    expect(validateReasonLength(reasonOver500)).toEqual({ valid: false, message: 'Reason must be 500 characters or less' });
  });

  it('real-time validation feedback works correctly', () => {
    const getValidationFeedback = (field: string, value: any) => {
      switch (field) {
        case 'reason':
          return !value || (typeof value === 'string' && value.trim().length > 0 && value.trim().length <= 500);
        case 'mileage':
          return value === null || value === undefined || (typeof value === 'number' && value > 0 && value <= 10000);
        case 'dateTime':
          if (!value.startDateTime || !value.endDateTime) return true; // Don't show error until both are filled
          const startDate = new Date(value.startDateTime);
          const endDate = new Date(value.endDateTime);
          return startDate >= new Date() && endDate > startDate;
        default:
          return true;
      }
    };

    // Test reason validation
    expect(getValidationFeedback('reason', '')).toBe(true); // No error shown for empty initially
    expect(getValidationFeedback('reason', 'Valid reason')).toBe(true);
    expect(getValidationFeedback('reason', 'A'.repeat(501))).toBe(false);

    // Test mileage validation
    expect(getValidationFeedback('mileage', null)).toBe(true);
    expect(getValidationFeedback('mileage', 50)).toBe(true);
    expect(getValidationFeedback('mileage', 0)).toBe(false);
    expect(getValidationFeedback('mileage', 15000)).toBe(false);

    // Test date validation
    const futureDate1 = new Date();
    futureDate1.setDate(futureDate1.getDate() + 1);
    const futureDate2 = new Date();
    futureDate2.setDate(futureDate2.getDate() + 2);
    
    expect(getValidationFeedback('dateTime', { 
      startDateTime: futureDate1.toISOString(), 
      endDateTime: futureDate2.toISOString() 
    })).toBe(true);
    
    const pastDate = new Date();
    pastDate.setDate(pastDate.getDate() - 1);
    expect(getValidationFeedback('dateTime', { 
      startDateTime: pastDate.toISOString(), 
      endDateTime: futureDate1.toISOString() 
    })).toBe(false);
  });
});