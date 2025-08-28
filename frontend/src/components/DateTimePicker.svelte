<script lang="ts">
  import { createEventDispatcher } from 'svelte';

  // Props
  export let startDateTime: string = '';
  export let duration: string = '';
  export let disabled: boolean = false;

  // Local state
  let startDate: string = '';
  let startTime: string = '';
  let validationErrors: string[] = [];

  // Get current date and time for validation
  const now = new Date();
  const today = now.toISOString().split('T')[0];
  const currentTime = now.toTimeString().slice(0, 5);

  // Event dispatcher
  const dispatch = createEventDispatcher<{
    dateTimeChanged: {
      startDateTime: string;
      endDateTime: string;
      returnDateTime: string;
      duration: string;
    };
  }>();

  // Validation and calculation
  $: {
    validationErrors = [];
    
    if (startDate && startTime && duration) {
      const start = new Date(`${startDate}T${startTime}`);
      
      // Validate start date/time is not in the past
      if (start < now) {
        validationErrors.push('Start date and time cannot be in the past');
      }
      
      // Calculate end date/time based on duration
      let end = new Date(start);
      let returnDate = new Date(start);
      
      switch (duration) {
        case '1h':
          end.setHours(end.getHours() + 1);
          returnDate = new Date(end);
          break;
        case '4h':
          end.setHours(end.getHours() + 4);
          returnDate = new Date(end);
          break;
        case '1d':
          end.setDate(end.getDate() + 1);
          returnDate = calculateReturnDate(end);
          break;
        case '2d':
          end.setDate(end.getDate() + 2);
          returnDate = calculateReturnDate(end);
          break;
        case '1w':
          end.setDate(end.getDate() + 7);
          returnDate = calculateReturnDate(end);
          break;
        default:
          validationErrors.push('Please select a valid duration');
          break;
      }
      
      if (validationErrors.length === 0 && duration !== '') {
        startDateTime = start.toISOString();
        
        dispatch('dateTimeChanged', {
          startDateTime: start.toISOString(),
          endDateTime: end.toISOString(),
          returnDateTime: returnDate.toISOString(),
          duration: duration
        });
      }
    }
  }

  function calculateReturnDate(endDate: Date): Date {
    const dayOfWeek = endDate.getDay(); // 0 = Sunday, 5 = Friday, 6 = Saturday
    
    if (dayOfWeek === 5) { // Friday
      const monday = new Date(endDate);
      monday.setDate(monday.getDate() + 3); // Add 3 days to get to Monday
      monday.setHours(9, 0, 0, 0); // Set to 9:00 AM
      return monday;
    } else if (dayOfWeek === 6 || dayOfWeek === 0) { // Saturday or Sunday
      const monday = new Date(endDate);
      const daysToAdd = dayOfWeek === 6 ? 2 : 1; // Saturday: add 2, Sunday: add 1
      monday.setDate(monday.getDate() + daysToAdd);
      monday.setHours(9, 0, 0, 0); // Set to 9:00 AM
      return monday;
    } else {
      return endDate; // Return same time for weekdays
    }
  }

  // Duration options
  const durationOptions = [
    { value: '', label: 'Select duration' },
    { value: '1h', label: '1 hour' },
    { value: '4h', label: '4 hours' },
    { value: '1d', label: '1 day' },
    { value: '2d', label: '2 days' },
    { value: '1w', label: '1 week' },
  ];
</script>

<div class="datetime-picker">
  <div class="form-row">
    <div class="form-group">
      <label for="start-date" class="form-label">
        Start Date <span class="required">*</span>
      </label>
      <input
        id="start-date"
        type="date"
        bind:value={startDate}
        min={today}
        {disabled}
        class="form-input"
        class:error={validationErrors.some(e => e.includes('date'))}
        aria-describedby="start-date-help"
        aria-invalid={validationErrors.some(e => e.includes('date'))}
        aria-required="true"
      />
      <div id="start-date-help" class="field-help">
        <span class="field-hint">Select a date (today or later)</span>
      </div>
    </div>

    <div class="form-group">
      <label for="start-time" class="form-label">
        Start Time <span class="required">*</span>
      </label>
      <input
        id="start-time"
        type="time"
        bind:value={startTime}
        min={startDate === today ? currentTime : ''}
        {disabled}
        class="form-input"
        class:error={validationErrors.some(e => e.includes('time'))}
        aria-describedby="start-time-help"
        aria-invalid={validationErrors.some(e => e.includes('time'))}
        aria-required="true"
      />
      <div id="start-time-help" class="field-help">
        <span class="field-hint">Select a time {startDate === today ? '(current time or later)' : ''}</span>
      </div>
    </div>
  </div>

  <div class="form-group">
    <label for="duration" class="form-label">
      Duration <span class="required">*</span>
    </label>
    <select 
      id="duration"
      bind:value={duration} 
      {disabled} 
      class="form-input"
      class:error={validationErrors.some(e => e.includes('duration'))}
      aria-describedby="duration-help"
      aria-invalid={validationErrors.some(e => e.includes('duration'))}
      aria-required="true"
    >
      {#each durationOptions as option}
        <option value={option.value}>{option.label}</option>
      {/each}
    </select>
    <div id="duration-help" class="field-help">
      <span class="field-hint">How long do you need the vehicle?</span>
    </div>
  </div>

  <!-- Validation Errors -->
  {#if validationErrors.length > 0}
    <div class="validation-errors" role="alert" aria-live="polite">
      {#each validationErrors as error}
        <div class="validation-error">
          <span class="error-icon" aria-hidden="true">⚠️</span>
          {error}
        </div>
      {/each}
    </div>
  {/if}

  {#if startDate && startTime && duration && validationErrors.length === 0}
    <div class="selected-dates" role="region" aria-label="Booking schedule summary">
      <h3>Booking Schedule:</h3>
      <p><strong>Start:</strong> {new Date(`${startDate}T${startTime}`).toLocaleString()}</p>
      <p><strong>Duration:</strong> {durationOptions.find(opt => opt.value === duration)?.label || duration}</p>
    </div>
  {/if}
</div>

<style>
  .datetime-picker {
    display: flex;
    flex-direction: column;
    gap: 1.5rem;
  }

  .form-row {
    display: flex;
    gap: 1rem;
    flex-wrap: wrap;
  }

  .form-group {
    display: flex;
    flex-direction: column;
    flex: 1;
    min-width: 200px;
  }

  .form-label {
    font-weight: 600;
    color: #374151;
    font-size: 0.875rem;
    margin-bottom: 0.5rem;
  }

  .required {
    color: #ef4444;
  }

  .form-input {
    padding: 0.75rem;
    border: 1px solid #d1d5db;
    border-radius: 0.375rem;
    font-size: 1rem;
    background-color: white;
    color: #1f2937;
    transition: border-color 0.2s, box-shadow 0.2s;
  }

  .form-input:focus {
    outline: none;
    border-color: #3b82f6;
    box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
    color: #1f2937;
  }

  .form-input:disabled {
    background-color: #f9fafb;
    color: #6b7280;
    cursor: not-allowed;
  }

  .form-input.error {
    border-color: #ef4444;
  }

  .form-input.error:focus {
    border-color: #ef4444;
    box-shadow: 0 0 0 3px rgba(239, 68, 68, 0.1);
  }

  .field-help {
    margin-top: 0.25rem;
  }

  .field-hint {
    font-size: 0.75rem;
    color: #6b7280;
    font-style: italic;
  }

  /* Specific styling for date/time inputs to ensure visibility */
  input[type="date"],
  input[type="time"] {
    color: #1f2937 !important;
    background-color: white !important;
  }

  input[type="date"]:focus,
  input[type="time"]:focus {
    color: #1f2937 !important;
  }

  /* Style the calendar/clock icons - make them visible */
  input[type="date"]::-webkit-calendar-picker-indicator {
    background: transparent;
    cursor: pointer;
    height: 20px;
    width: 20px;
    border: 1px solid #6b7280;
    border-radius: 3px;
    background-color: #f9fafb;
    background-image: url("data:image/svg+xml,%3csvg xmlns='http://www.w3.org/2000/svg' fill='%236b7280' viewBox='0 0 20 20'%3e%3cpath fill-rule='evenodd' d='M6 2a1 1 0 00-1 1v1H4a2 2 0 00-2 2v10a2 2 0 002 2h12a2 2 0 002-2V6a2 2 0 00-2-2h-1V3a1 1 0 10-2 0v1H7V3a1 1 0 00-1-1zm0 5a1 1 0 000 2h8a1 1 0 100-2H6z' clip-rule='evenodd'/%3e%3c/svg%3e");
    background-repeat: no-repeat;
    background-position: center;
    background-size: 16px 16px;
  }

  input[type="time"]::-webkit-calendar-picker-indicator {
    background: transparent;
    cursor: pointer;
    height: 20px;
    width: 20px;
    border: 1px solid #6b7280;
    border-radius: 3px;
    background-color: #f9fafb;
    background-image: url("data:image/svg+xml,%3csvg xmlns='http://www.w3.org/2000/svg' fill='%236b7280' viewBox='0 0 20 20'%3e%3cpath fill-rule='evenodd' d='M10 18a8 8 0 100-16 8 8 0 000 16zm1-12a1 1 0 10-2 0v4a1 1 0 00.293.707l2.828 2.829a1 1 0 101.415-1.415L11 9.586V6z' clip-rule='evenodd'/%3e%3c/svg%3e");
    background-repeat: no-repeat;
    background-position: center;
    background-size: 14px 14px;
  }

  input[type="date"]::-webkit-calendar-picker-indicator:hover,
  input[type="time"]::-webkit-calendar-picker-indicator:hover {
    background-color: #e5e7eb;
    border-color: #374151;
  }

  /* For webkit browsers - ensure text is dark */
  input[type="date"]::-webkit-datetime-edit,
  input[type="date"]::-webkit-datetime-edit-text,
  input[type="date"]::-webkit-datetime-edit-month-field,
  input[type="date"]::-webkit-datetime-edit-day-field,
  input[type="date"]::-webkit-datetime-edit-year-field,
  input[type="time"]::-webkit-datetime-edit,
  input[type="time"]::-webkit-datetime-edit-text,
  input[type="time"]::-webkit-datetime-edit-hour-field,
  input[type="time"]::-webkit-datetime-edit-minute-field {
    color: #1f2937 !important;
  }

  .selected-dates {
    margin-top: 1rem;
    padding: 1rem;
    background-color: #f0fdf4;
    border: 1px solid #22c55e;
    border-radius: 0.375rem;
  }

  .selected-dates h3 {
    margin: 0 0 0.5rem 0;
    color: #15803d;
    font-size: 1rem;
    font-weight: 600;
  }

  .selected-dates p {
    margin: 0.25rem 0;
    color: #15803d;
    font-size: 0.875rem;
  }

  .validation-errors {
    margin-top: 1rem;
    padding: 0.75rem;
    background-color: #fef2f2;
    border: 1px solid #fecaca;
    border-left: 4px solid #ef4444;
    border-radius: 0.375rem;
  }

  .validation-error {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    color: #991b1b;
    font-size: 0.875rem;
    margin-bottom: 0.25rem;
  }

  .validation-error:last-child {
    margin-bottom: 0;
  }

  .error-icon {
    flex-shrink: 0;
  }

  /* Responsive design */
  @media (max-width: 640px) {
    .form-row {
      flex-direction: column;
    }
    
    .form-group {
      min-width: unset;
    }
  }
</style>