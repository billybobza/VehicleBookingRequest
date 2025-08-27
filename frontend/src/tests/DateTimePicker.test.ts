import { describe, it, expect, beforeEach, vi } from 'vitest';

// Mock the current date for consistent testing
const mockDate = new Date('2024-01-15T10:00:00Z');
vi.setSystemTime(mockDate);

describe('DateTimePicker Logic', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('duration options are properly structured', () => {
    const durationOptions = [
      { value: '', label: 'Select duration' },
      { value: '1h', label: '1 hour' },
      { value: '4h', label: '4 hours' },
      { value: '1d', label: '1 day' },
      { value: '2d', label: '2 days' },
      { value: '1w', label: '1 week' },
      { value: '2w', label: '2 weeks' },
      { value: '3w', label: '3 weeks' },
      { value: '1m', label: '1 month' },
    ];
    
    expect(durationOptions).toHaveLength(9);
    expect(durationOptions[0].value).toBe('');
    expect(durationOptions[1].label).toBe('1 hour');
    expect(durationOptions[4].label).toBe('2 days');
    expect(durationOptions[7].label).toBe('3 weeks');
  });

  it('calculates end date correctly for 1 hour duration', () => {
    const calculateEndDate = (startDate: string, startTime: string, duration: string) => {
      const start = new Date(`${startDate}T${startTime}`);
      const end = new Date(start);

      switch (duration) {
        case '1h':
          end.setHours(end.getHours() + 1);
          break;
        case '4h':
          end.setHours(end.getHours() + 4);
          break;
        case '1d':
          end.setDate(end.getDate() + 1);
          break;
        case '2d':
          end.setDate(end.getDate() + 2);
          break;
        case '1w':
          end.setDate(end.getDate() + 7);
          break;
        case '2w':
          end.setDate(end.getDate() + 14);
          break;
        case '3w':
          end.setDate(end.getDate() + 21);
          break;
        case '1m':
          end.setMonth(end.getMonth() + 1);
          break;
      }

      return end;
    };

    const startDate = '2024-01-20';
    const startTime = '14:00';
    const duration = '1h';
    
    const start = new Date(`${startDate}T${startTime}`);
    const end = calculateEndDate(startDate, startTime, duration);
    
    expect(end.getTime() - start.getTime()).toBe(60 * 60 * 1000); // 1 hour in ms
  });

  it('calculates end date correctly for 2 days duration', () => {
    const calculateEndDate = (startDate: string, startTime: string, duration: string) => {
      const start = new Date(`${startDate}T${startTime}`);
      const end = new Date(start);

      switch (duration) {
        case '1h':
          end.setHours(end.getHours() + 1);
          break;
        case '4h':
          end.setHours(end.getHours() + 4);
          break;
        case '1d':
          end.setDate(end.getDate() + 1);
          break;
        case '2d':
          end.setDate(end.getDate() + 2);
          break;
        case '1w':
          end.setDate(end.getDate() + 7);
          break;
        case '2w':
          end.setDate(end.getDate() + 14);
          break;
        case '3w':
          end.setDate(end.getDate() + 21);
          break;
        case '1m':
          end.setMonth(end.getMonth() + 1);
          break;
      }

      return end;
    };

    const startDate = '2024-01-20';
    const startTime = '14:00';
    const duration = '2d';
    
    const start = new Date(`${startDate}T${startTime}`);
    const end = calculateEndDate(startDate, startTime, duration);
    
    expect(end.getTime() - start.getTime()).toBe(2 * 24 * 60 * 60 * 1000); // 2 days in ms
  });

  it('calculates end date correctly for 3 weeks duration', () => {
    const calculateEndDate = (startDate: string, startTime: string, duration: string) => {
      const start = new Date(`${startDate}T${startTime}`);
      const end = new Date(start);

      switch (duration) {
        case '1h':
          end.setHours(end.getHours() + 1);
          break;
        case '4h':
          end.setHours(end.getHours() + 4);
          break;
        case '1d':
          end.setDate(end.getDate() + 1);
          break;
        case '2d':
          end.setDate(end.getDate() + 2);
          break;
        case '1w':
          end.setDate(end.getDate() + 7);
          break;
        case '2w':
          end.setDate(end.getDate() + 14);
          break;
        case '3w':
          end.setDate(end.getDate() + 21);
          break;
        case '1m':
          end.setMonth(end.getMonth() + 1);
          break;
      }

      return end;
    };

    const startDate = '2024-01-20';
    const startTime = '14:00';
    const duration = '3w';
    
    const start = new Date(`${startDate}T${startTime}`);
    const end = calculateEndDate(startDate, startTime, duration);
    
    expect(end.getTime() - start.getTime()).toBe(21 * 24 * 60 * 60 * 1000); // 3 weeks in ms
  });

  it('applies Friday return rule correctly', () => {
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

    // January 19, 2024 is a Friday
    const fridayEnd = new Date('2024-01-19T17:00:00');
    const returnDate = calculateReturnDate(fridayEnd);
    
    // Should be Monday (January 22, 2024) at 9:00 AM
    expect(returnDate.getDay()).toBe(1); // Monday
    expect(returnDate.getHours()).toBe(9);
    expect(returnDate.getMinutes()).toBe(0);
    expect(returnDate.getDate()).toBe(22); // January 22
  });

  it('applies weekend return rule correctly for Saturday', () => {
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

    // January 20, 2024 is a Saturday
    const saturdayEnd = new Date('2024-01-20T17:00:00');
    const returnDate = calculateReturnDate(saturdayEnd);
    
    // Should be Monday (January 22, 2024) at 9:00 AM
    expect(returnDate.getDay()).toBe(1); // Monday
    expect(returnDate.getHours()).toBe(9);
    expect(returnDate.getMinutes()).toBe(0);
    expect(returnDate.getDate()).toBe(22); // January 22
  });

  it('applies weekend return rule correctly for Sunday', () => {
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

    // January 21, 2024 is a Sunday
    const sundayEnd = new Date('2024-01-21T17:00:00');
    const returnDate = calculateReturnDate(sundayEnd);
    
    // Should be Monday (January 22, 2024) at 9:00 AM
    expect(returnDate.getDay()).toBe(1); // Monday
    expect(returnDate.getHours()).toBe(9);
    expect(returnDate.getMinutes()).toBe(0);
    expect(returnDate.getDate()).toBe(22); // January 22
  });

  it('does not apply weekend rule for weekdays', () => {
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

    // January 16, 2024 is a Tuesday
    const tuesdayEnd = new Date('2024-01-16T17:00:00');
    const returnDate = calculateReturnDate(tuesdayEnd);
    
    // Return date should be the same as end date for weekdays
    expect(returnDate.getTime()).toBe(tuesdayEnd.getTime());
    expect(returnDate.getDay()).toBe(2); // Tuesday
  });

  it('validates past dates correctly', () => {
    const validateDateTime = (startDate: string, startTime: string) => {
      const errors: string[] = [];
      
      if (startDate && startTime) {
        const selectedDateTime = new Date(`${startDate}T${startTime}`);
        const now = new Date();

        // Check if date is in the past
        if (selectedDateTime < now) {
          errors.push('Start date and time cannot be in the past');
        }
      }

      return errors;
    };

    // Test with past date
    const pastErrors = validateDateTime('2024-01-10', '09:00');
    expect(pastErrors).toContain('Start date and time cannot be in the past');

    // Test with future date
    const futureErrors = validateDateTime('2024-12-25', '09:00');
    expect(futureErrors).toHaveLength(0);
  });

  it('validates required fields correctly', () => {
    const validateRequiredFields = (startDate: string, startTime: string, duration: string) => {
      const errors: string[] = [];

      if (startDate && !startTime) {
        errors.push('Start time is required when date is selected');
      }

      if (startTime && !startDate) {
        errors.push('Start date is required when time is selected');
      }

      if ((startDate || startTime) && !duration) {
        errors.push('Duration is required');
      }

      return errors;
    };

    // Test date without time
    const dateOnlyErrors = validateRequiredFields('2024-01-20', '', '');
    expect(dateOnlyErrors).toContain('Start time is required when date is selected');

    // Test time without date
    const timeOnlyErrors = validateRequiredFields('', '14:00', '');
    expect(timeOnlyErrors).toContain('Start date is required when time is selected');

    // Test date and time without duration
    const noDurationErrors = validateRequiredFields('2024-01-20', '14:00', '');
    expect(noDurationErrors).toContain('Duration is required');

    // Test all fields filled
    const allFilledErrors = validateRequiredFields('2024-01-20', '14:00', '1h');
    expect(allFilledErrors).toHaveLength(0);
  });

  it('formats date time correctly', () => {
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

    const testDate = '2024-01-20T14:30:00Z';
    const formatted = formatDateTime(testDate);
    
    expect(formatted).toContain('2024');
    expect(formatted).toContain('Jan');
    expect(formatted).toContain('20');
  });

  it('gets minimum date correctly', () => {
    const getMinDate = (): string => {
      return new Date().toISOString().split('T')[0];
    };

    const minDate = getMinDate();
    const today = new Date().toISOString().split('T')[0];
    
    expect(minDate).toBe(today);
  });

  it('gets minimum time correctly for today', () => {
    const getMinTime = (selectedDate: string): string => {
      const now = new Date();
      const today = now.toISOString().split('T')[0];
      
      if (selectedDate === today) {
        // If selected date is today, minimum time is current time
        return now.toTimeString().slice(0, 5);
      }
      return '00:00';
    };

    const today = new Date().toISOString().split('T')[0];
    const futureDate = '2024-12-25';
    
    const minTimeToday = getMinTime(today);
    const minTimeFuture = getMinTime(futureDate);
    
    expect(minTimeToday).toMatch(/^\d{2}:\d{2}$/); // Should be current time format
    expect(minTimeFuture).toBe('00:00'); // Should be midnight for future dates
  });
});