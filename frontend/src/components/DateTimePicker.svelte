<script lang="ts">
  import { createEventDispatcher } from 'svelte';

  // Props
  export let startDateTime: string = '';
  export let duration: string = '';
  export let disabled: boolean = false;

  // Local state
  let startDate: string = '';
  let startTime: string = '';

  // Event dispatcher
  const dispatch = createEventDispatcher<{
    dateTimeChanged: {
      startDateTime: string;
      endDateTime: string;
      returnDateTime: string;
      duration: string;
    };
  }>();

  // Simple reactive calculation
  $: if (startDate && startTime && duration) {
    const start = new Date(`${startDate}T${startTime}`);
    startDateTime = start.toISOString();
    
    // Dispatch simple event for now
    dispatch('dateTimeChanged', {
      startDateTime: startDateTime,
      endDateTime: startDateTime, // placeholder
      returnDateTime: startDateTime, // placeholder  
      duration: duration
    });
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
        {disabled}
        class="form-input"
      />
    </div>

    <div class="form-group">
      <label for="start-time" class="form-label">
        Start Time <span class="required">*</span>
      </label>
      <input
        id="start-time"
        type="time"
        bind:value={startTime}
        {disabled}
        class="form-input"
      />
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
    >
      {#each durationOptions as option}
        <option value={option.value}>{option.label}</option>
      {/each}
    </select>
  </div>

  {#if startDate && startTime && duration}
    <div class="selected-dates">
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