<script lang="ts">
  import { onMount } from 'svelte';
  import VehicleSelector from './VehicleSelector.svelte';
  import DateTimePicker from './DateTimePicker.svelte';
  import LoadingSpinner from './LoadingSpinner.svelte';
  import ErrorMessage from './ErrorMessage.svelte';
  import { apiService, type Vehicle, type BookingRequest, type BookingConfirmation } from '../services/api';
  import { addError } from '../stores/ui';

  // Form state
  let selectedVehicleId: number | null = null;
  let selectedVehicle: Vehicle | null = null;
  let startDateTime: string = '';
  let endDateTime: string = '';
  let returnDateTime: string = '';
  let duration: string = '';
  let reason: string = '';
  let estimatedMileage: number | null = null;

  // UI state
  let isSubmitting = false;
  let isFormValid = false;
  let bookingConfirmation: BookingConfirmation | null = null;
  let formErrors: string[] = [];
  let showValidationErrors = false;

  // Form validation - only compute validity, don't show errors until needed
  $: isFormValid = validateForm(selectedVehicleId, startDateTime, endDateTime, reason, estimatedMileage);

  function validateForm(vehicleId: number | null, startDT: string, endDT: string, reasonText: string, mileage: number | null): boolean {
    // Check validity of all form fields
    const hasVehicle = !!vehicleId;
    const hasDateTime = !!(startDT && endDT);
    const hasReason = !!(reasonText && reasonText.trim().length > 0);
    const hasMileage = mileage !== null && mileage !== undefined && mileage > 0;
    
    return hasVehicle && hasDateTime && hasReason && hasMileage;
  }

  function getFormErrors(): string[] {
    const errors: string[] = [];

    // Vehicle selection validation
    if (!selectedVehicleId) {
      errors.push('Please select a vehicle');
    }

    // Date/time validation
    if (!startDateTime || !endDateTime) {
      errors.push('Please select start date, time, and duration');
    }

    // Reason validation
    if (!reason || reason.trim().length === 0) {
      errors.push('Please provide a reason for vehicle usage');
    }

    // Estimated mileage validation
    if (estimatedMileage === null || estimatedMileage === undefined) {
      errors.push('Please provide estimated mileage');
    } else if (estimatedMileage <= 0) {
      errors.push('Estimated mileage must be a positive number');
    }

    return errors;
  }

  // Update formErrors only when we need to show them
  $: if (showValidationErrors) {
    formErrors = getFormErrors();
  } else {
    formErrors = [];
  }

  function handleVehicleSelected(event: CustomEvent<{ vehicleId: number; vehicle: Vehicle }>) {
    selectedVehicleId = event.detail.vehicleId;
    selectedVehicle = event.detail.vehicle;
  }

  function handleDateTimeChanged(event: CustomEvent<{
    startDateTime: string;
    endDateTime: string;
    returnDateTime: string;
    duration: string;
  }>) {
    startDateTime = event.detail.startDateTime;
    endDateTime = event.detail.endDateTime;
    returnDateTime = event.detail.returnDateTime;
    duration = event.detail.duration;
  }


  async function handleSubmit(event: Event) {
    event.preventDefault();
    
    // Show validation errors when user tries to submit
    showValidationErrors = true;
    
    if (!isFormValid || isSubmitting) {
      return;
    }

    isSubmitting = true;

    try {
      const bookingRequest: BookingRequest = {
        vehicle_id: selectedVehicleId!,
        start_datetime: startDateTime,
        end_datetime: endDateTime,
        reason: reason.trim(),
        estimated_mileage: estimatedMileage!,
      };

      const response = await apiService.createBooking(bookingRequest);

      if (response.error) {
        addError({
          code: response.error.code,
          message: response.error.message,
          details: response.error.details,
        });
      } else if (response.data) {
        bookingConfirmation = response.data;
        // Reset form after successful submission
        resetForm();
      }
    } catch (error) {
      addError({
        code: 'SUBMISSION_ERROR',
        message: 'Failed to submit booking request. Please try again.',
      });
    } finally {
      isSubmitting = false;
    }
  }

  function resetForm() {
    selectedVehicleId = null;
    selectedVehicle = null;
    startDateTime = '';
    endDateTime = '';
    returnDateTime = '';
    duration = '';
    reason = '';
    estimatedMileage = null;
    formErrors = [];
    showValidationErrors = false;
  }

  function startNewBooking() {
    bookingConfirmation = null;
    resetForm();
  }

  function formatDateTime(isoString: string): string {
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
  }
</script>

{#if bookingConfirmation}
  <!-- Booking Confirmation Display -->
  <div class="booking-confirmation">
    <div class="confirmation-header">
      <h1>Booking Confirmed!</h1>
      <div class="confirmation-icon">✓</div>
    </div>
    
    <div class="confirmation-details">
      <h2>Booking Details</h2>
      
      <div class="detail-row">
        <span class="detail-label">Confirmation Number:</span>
        <span class="detail-value confirmation-number">#{bookingConfirmation.id}</span>
      </div>
      
      <div class="detail-row">
        <span class="detail-label">Vehicle:</span>
        <span class="detail-value">
          {selectedVehicle ? `${selectedVehicle.registration} - ${selectedVehicle.make} (${selectedVehicle.color})` : 'N/A'}
        </span>
      </div>
      
      <div class="detail-row">
        <span class="detail-label">Start:</span>
        <span class="detail-value">{formatDateTime(bookingConfirmation.start_datetime)}</span>
      </div>
      
      <div class="detail-row">
        <span class="detail-label">End:</span>
        <span class="detail-value">{formatDateTime(bookingConfirmation.end_datetime)}</span>
      </div>
      
      <div class="detail-row">
        <span class="detail-label">Return:</span>
        <span class="detail-value return-date">{formatDateTime(bookingConfirmation.return_datetime)}</span>
      </div>
      
      <div class="detail-row">
        <span class="detail-label">Reason:</span>
        <span class="detail-value">{bookingConfirmation.reason}</span>
      </div>
      
      <div class="detail-row">
        <span class="detail-label">Estimated Mileage:</span>
        <span class="detail-value">{bookingConfirmation.estimated_mileage} miles</span>
      </div>
      
      <div class="detail-row">
        <span class="detail-label">Status:</span>
        <span class="detail-value status">{bookingConfirmation.status}</span>
      </div>
    </div>
    
    <button class="new-booking-btn" on:click={startNewBooking}>
      Make Another Booking
    </button>
  </div>
{:else}
  <!-- Booking Form -->
  <div class="booking-form-container">
    <div class="form-header">
      <h1>Vehicle Booking Request</h1>
      <p>Complete the form below to request a company vehicle.</p>
    </div>

    <form on:submit={handleSubmit} class="booking-form">
      <!-- Vehicle Selection -->
      <VehicleSelector
        bind:selectedVehicleId
        startDate={startDateTime ? new Date(startDateTime).toISOString().split('T')[0] : ''}
        endDate={endDateTime ? new Date(endDateTime).toISOString().split('T')[0] : ''}
        disabled={isSubmitting}
        on:vehicleSelected={handleVehicleSelected}
      />
      
      <!-- Selected Vehicle Details -->
      {#if selectedVehicle}
        <div class="selected-vehicle">
          <h3>Selected Vehicle:</h3>
          <p><strong>Registration:</strong> {selectedVehicle.registration}</p>
          <p><strong>Make:</strong> {selectedVehicle.make}</p>
          <p><strong>Color:</strong> {selectedVehicle.color}</p>
        </div>
      {/if}

      <!-- Date and Time Selection -->
      <DateTimePicker
        bind:startDateTime
        bind:duration
        disabled={isSubmitting}
        on:dateTimeChanged={handleDateTimeChanged}
      />

      <!-- Reason for Usage -->
      <div class="form-group">
        <label for="reason" class="form-label">
          Reason for Usage <span class="required">*</span>
        </label>
        <textarea
          id="reason"
          bind:value={reason}
          placeholder="Please describe the purpose of your vehicle usage..."
          disabled={isSubmitting}
          class="form-textarea"
          class:error={showValidationErrors && formErrors.some(e => e.includes('reason'))}
          rows="3"
        ></textarea>
      </div>

      <!-- Estimated Mileage -->
      <div class="form-group">
        <label for="estimated-mileage" class="form-label">
          Estimated Mileage <span class="required">*</span>
        </label>
        <div class="input-with-unit">
          <input
            id="estimated-mileage"
            type="number"
            bind:value={estimatedMileage}
            placeholder="Enter estimated miles"
            min="1"
            step="1"
            disabled={isSubmitting}
            class="form-input"
            class:error={showValidationErrors && formErrors.some(e => e.includes('mileage'))}
          />
          <span class="input-unit">miles</span>
        </div>
      </div>

      <!-- Form Errors -->
      {#if showValidationErrors && formErrors.length > 0}
        <div class="form-errors">
          {#each formErrors as error}
            <ErrorMessage message={error} />
          {/each}
        </div>
      {/if}

      <!-- Submit Button -->
      <div class="form-actions">
        <button
          type="submit"
          disabled={!isFormValid || isSubmitting}
          class="submit-btn"
          class:loading={isSubmitting}
        >
          {#if isSubmitting}
            <LoadingSpinner size="small" inline={true} />
            Submitting Request...
          {:else}
            Submit Booking Request
          {/if}
        </button>
      </div>
    </form>
  </div>
{/if}

<style>
  .booking-form-container {
    max-width: 600px;
    margin: 0 auto;
    padding: 2rem;
    background-color: white;
    border-radius: 0.5rem;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  }

  .form-header {
    text-align: center;
    margin-bottom: 2rem;
  }

  .form-header h1 {
    color: #1f2937;
    font-size: 2rem;
    font-weight: 700;
    margin: 0 0 0.5rem 0;
  }

  .form-header p {
    color: #6b7280;
    font-size: 1rem;
    margin: 0;
  }

  .booking-form {
    display: flex;
    flex-direction: column;
    gap: 1.5rem;
  }

  .form-group {
    display: flex;
    flex-direction: column;
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

  .form-input,
  .form-textarea {
    padding: 0.75rem;
    border: 1px solid #d1d5db;
    border-radius: 0.375rem;
    font-size: 1rem;
    background-color: white;
    color: #1f2937;
    transition: border-color 0.2s, box-shadow 0.2s;
  }

  .form-input:focus,
  .form-textarea:focus {
    outline: none;
    border-color: #3b82f6;
    box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
    color: #1f2937;
  }

  .form-input:disabled,
  .form-textarea:disabled {
    background-color: #f9fafb;
    color: #6b7280;
    cursor: not-allowed;
  }

  .form-input.error,
  .form-textarea.error {
    border-color: #ef4444;
  }

  .form-input.error:focus,
  .form-textarea.error:focus {
    border-color: #ef4444;
    box-shadow: 0 0 0 3px rgba(239, 68, 68, 0.1);
  }

  .form-textarea {
    resize: vertical;
    min-height: 80px;
  }

  .input-with-unit {
    position: relative;
    display: flex;
    align-items: center;
  }

  .input-with-unit .form-input {
    flex: 1;
    padding-right: 3rem;
  }

  .input-unit {
    position: absolute;
    right: 0.75rem;
    color: #6b7280;
    font-size: 0.875rem;
    pointer-events: none;
  }

  .form-errors {
    margin: -0.5rem 0 0 0;
  }

  .form-actions {
    margin-top: 1rem;
  }

  .submit-btn {
    width: 100%;
    padding: 0.875rem 1.5rem;
    background-color: #3b82f6;
    color: white;
    border: none;
    border-radius: 0.375rem;
    font-size: 1rem;
    font-weight: 600;
    cursor: pointer;
    transition: background-color 0.2s, opacity 0.2s;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 0.5rem;
  }

  .submit-btn:hover:not(:disabled) {
    background-color: #2563eb;
  }

  .submit-btn:disabled {
    background-color: #9ca3af;
    cursor: not-allowed;
    opacity: 0.6;
  }

  .submit-btn.loading {
    cursor: wait;
  }

  /* Booking Confirmation Styles */
  .booking-confirmation {
    max-width: 600px;
    margin: 0 auto;
    padding: 2rem;
    background-color: white;
    border-radius: 0.5rem;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  }

  .confirmation-header {
    text-align: center;
    margin-bottom: 2rem;
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 1rem;
  }

  .confirmation-header h1 {
    color: #059669;
    font-size: 2rem;
    font-weight: 700;
    margin: 0;
  }

  .confirmation-icon {
    width: 4rem;
    height: 4rem;
    background-color: #059669;
    color: white;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 2rem;
    font-weight: bold;
  }

  .confirmation-details {
    margin-bottom: 2rem;
  }

  .confirmation-details h2 {
    color: #1f2937;
    font-size: 1.25rem;
    font-weight: 600;
    margin: 0 0 1rem 0;
    border-bottom: 2px solid #e5e7eb;
    padding-bottom: 0.5rem;
  }

  .detail-row {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    padding: 0.75rem 0;
    border-bottom: 1px solid #f3f4f6;
  }

  .detail-row:last-child {
    border-bottom: none;
  }

  .detail-label {
    font-weight: 600;
    color: #4b5563;
    flex-shrink: 0;
    margin-right: 1rem;
  }

  .detail-value {
    color: #1f2937;
    text-align: right;
    flex: 1;
  }

  .confirmation-number {
    font-family: monospace;
    font-weight: 700;
    color: #3b82f6;
  }

  .return-date {
    color: #059669;
    font-weight: 500;
  }

  .status {
    text-transform: capitalize;
    font-weight: 600;
    color: #059669;
  }

  .new-booking-btn {
    width: 100%;
    padding: 0.875rem 1.5rem;
    background-color: #6b7280;
    color: white;
    border: none;
    border-radius: 0.375rem;
    font-size: 1rem;
    font-weight: 600;
    cursor: pointer;
    transition: background-color 0.2s;
  }

  .new-booking-btn:hover {
    background-color: #4b5563;
  }

  /* Selected Vehicle Styles */
  .selected-vehicle {
    margin: 1rem 0;
    padding: 1rem;
    background-color: #f0f9ff;
    border: 1px solid #0ea5e9;
    border-radius: 0.375rem;
  }

  .selected-vehicle h3 {
    margin: 0 0 0.5rem 0;
    color: #0c4a6e;
    font-size: 1rem;
    font-weight: 600;
  }

  .selected-vehicle p {
    margin: 0.25rem 0;
    color: #0c4a6e;
    font-size: 0.875rem;
  }

  /* Responsive design */
  @media (max-width: 640px) {
    .booking-form-container,
    .booking-confirmation {
      margin: 1rem;
      padding: 1rem;
    }

    .form-header h1 {
      font-size: 1.5rem;
    }

    .detail-row {
      flex-direction: column;
      gap: 0.25rem;
    }

    .detail-value {
      text-align: left;
    }

    .confirmation-header {
      gap: 0.5rem;
    }

    .confirmation-icon {
      width: 3rem;
      height: 3rem;
      font-size: 1.5rem;
    }
  }
</style>