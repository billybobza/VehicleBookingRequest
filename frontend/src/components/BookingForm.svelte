<script lang="ts">
  import { onMount } from 'svelte';
  import VehicleSelector from './VehicleSelector.svelte';
  import DateTimePicker from './DateTimePicker.svelte';
  import LoadingSpinner from './LoadingSpinner.svelte';
  import ErrorMessage from './ErrorMessage.svelte';
  import { apiService, type Vehicle, type BookingRequest, type BookingConfirmation } from '../services/api';
  import { addError, addSuccess, setLoading } from '../stores/ui';

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
  
  // Form validation state tracking

  function validateForm(vehicleId: number | null, startDT: string, endDT: string, reasonText: string, mileage: number | null): boolean {
    // Check validity of all form fields
    const hasVehicle = !!vehicleId;
    const hasDateTime = !!(startDT && endDT);
    const hasReason = !!(reasonText && reasonText.trim().length > 0);
    const hasMileage = mileage !== null && mileage !== undefined && mileage > 0;
    
    // Additional validation for date/time
    if (hasDateTime) {
      const startDate = new Date(startDT);
      const endDate = new Date(endDT);
      const now = new Date();
      
      // Check if start date is in the past
      if (startDate < now) {
        return false;
      }
      
      // Check if end date is after start date
      if (endDate <= startDate) {
        return false;
      }
    }
    
    // Additional validation for reason length
    if (hasReason && reasonText.trim().length > 500) {
      return false;
    }
    
    // Additional validation for mileage range
    if (hasMileage && (mileage > 10000)) {
      return false;
    }
    
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
    } else {
      const startDate = new Date(startDateTime);
      const endDate = new Date(endDateTime);
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
    if (!reason || reason.trim().length === 0) {
      errors.push('Please provide a reason for vehicle usage');
    } else if (reason.trim().length > 500) {
      errors.push('Reason must be 500 characters or less');
    }

    // Estimated mileage validation
    if (estimatedMileage === null || estimatedMileage === undefined) {
      errors.push('Please provide estimated mileage');
    } else if (estimatedMileage <= 0) {
      errors.push('Estimated mileage must be a positive number');
    } else if (estimatedMileage > 10000) {
      errors.push('Estimated mileage cannot exceed 10,000 miles');
    }

    return errors;
  }

  // Update formErrors only when we need to show them
  $: if (showValidationErrors) {
    formErrors = getFormErrors();
  } else {
    formErrors = [];
  }

  // Real-time validation feedback for individual fields (without showing errors until submit)
  $: reasonValid = !reason || (reason.trim().length > 0 && reason.trim().length <= 500);
  $: mileageValid = estimatedMileage === null || estimatedMileage === undefined || (estimatedMileage > 0 && estimatedMileage <= 10000);
  $: dateTimeValid = !startDateTime || !endDateTime || (new Date(startDateTime) >= new Date() && new Date(endDateTime) > new Date(startDateTime));

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
    setLoading('booking-submission', true);

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
        // Provide user-friendly error messages based on error codes
        let userMessage = response.error.message;
        
        switch (response.error.code) {
          case 'HTTP_400':
            userMessage = 'Invalid booking data. Please check your inputs and try again.';
            break;
          case 'HTTP_404':
            userMessage = 'The selected vehicle is no longer available. Please choose another vehicle.';
            break;
          case 'HTTP_422':
          case 'VALIDATION_ERROR':
            userMessage = 'Please check your form inputs. Some fields contain invalid data.';
            // If we have validation details, show specific field errors
            if (response.error.details && Array.isArray(response.error.details)) {
              const fieldErrors = response.error.details.map((detail: any) => {
                const field = detail.loc ? detail.loc[detail.loc.length - 1] : 'field';
                return `${field}: ${detail.msg}`;
              }).join(', ');
              userMessage += ` Details: ${fieldErrors}`;
            }
            break;
          case 'HTTP_409':
            userMessage = 'This vehicle is already booked for the selected time period. Please choose different dates or another vehicle.';
            break;
          case 'HTTP_500':
          case 'DATABASE_ERROR':
          case 'INTERNAL_SERVER_ERROR':
            userMessage = 'A server error occurred. Please try again later or contact support if the problem persists.';
            break;
          case 'NETWORK_ERROR':
            userMessage = 'Unable to connect to the server. Please check your internet connection and try again.';
            break;
          default:
            // Use the original message if we don't have a specific mapping
            userMessage = response.error.message || 'An unexpected error occurred while processing your booking.';
        }
        
        addError({
          code: response.error.code,
          message: userMessage,
          details: response.error.details,
        });
      } else if (response.data) {
        bookingConfirmation = response.data;
        addSuccess(`Booking confirmed! Your confirmation number is #${response.data.id}`);
        // Reset form after successful submission
        resetForm();
      } else {
        // Handle unexpected response format
        addError({
          code: 'UNEXPECTED_RESPONSE',
          message: 'Received an unexpected response from the server. Please try again.',
        });
      }
    } catch (error) {
      // Handle network errors and other exceptions
      let errorMessage = 'Failed to submit booking request. Please try again.';
      let errorCode = 'SUBMISSION_ERROR';
      
      if (error instanceof TypeError && error.message.includes('fetch')) {
        errorMessage = 'Unable to connect to the server. Please check your internet connection and try again.';
        errorCode = 'NETWORK_ERROR';
      } else if (error instanceof Error) {
        errorMessage = `An error occurred: ${error.message}`;
        errorCode = 'CLIENT_ERROR';
      }
      
      addError({
        code: errorCode,
        message: errorMessage,
      });
    } finally {
      isSubmitting = false;
      setLoading('booking-submission', false);
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
  <div class="card max-w-4xl mx-auto">
    <div class="text-center mb-8">
      <div class="bg-green-100 rounded-full p-4 w-20 h-20 mx-auto mb-4">
        <svg class="w-12 h-12 text-green-600 mx-auto" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path>
        </svg>
      </div>
      <h1 class="text-3xl font-bold text-green-600 mb-2">Booking Confirmed!</h1>
      <p class="text-lg text-gray-600">Your vehicle booking has been successfully submitted.</p>
    </div>
    
    <div class="bg-gray-50 rounded-lg p-6 mb-8">
      <h2 class="text-xl font-semibold text-gray-900 mb-6 flex items-center">
        <svg class="w-5 h-5 text-primary-600 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path>
        </svg>
        Booking Details
      </h2>
      
      <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div class="space-y-4">
          <div class="bg-white p-4 rounded-lg border">
            <div class="text-sm font-medium text-gray-500 mb-1">Confirmation Number</div>
            <div class="text-lg font-bold text-primary-600">#{bookingConfirmation.id}</div>
          </div>
          
          <div class="bg-white p-4 rounded-lg border">
            <div class="text-sm font-medium text-gray-500 mb-1">Vehicle</div>
            {#if selectedVehicle}
              <div class="text-lg font-semibold text-gray-900">{selectedVehicle.registration}</div>
              <div class="text-sm text-gray-600">{selectedVehicle.make} • {selectedVehicle.color}</div>
            {:else}
              <div class="text-gray-600">N/A</div>
            {/if}
          </div>
          
          <div class="bg-white p-4 rounded-lg border">
            <div class="text-sm font-medium text-gray-500 mb-1">Status</div>
            <div class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
              {bookingConfirmation.status}
            </div>
          </div>
        </div>
        
        <div class="space-y-4">
          <div class="bg-white p-4 rounded-lg border">
            <div class="text-sm font-medium text-gray-500 mb-1">Start Date & Time</div>
            <div class="text-lg text-gray-900">{formatDateTime(bookingConfirmation.start_datetime)}</div>
          </div>
          
          <div class="bg-white p-4 rounded-lg border">
            <div class="text-sm font-medium text-gray-500 mb-1">End Date & Time</div>
            <div class="text-lg text-gray-900">{formatDateTime(bookingConfirmation.end_datetime)}</div>
          </div>
          
          <div class="bg-white p-4 rounded-lg border">
            <div class="text-sm font-medium text-gray-500 mb-1">Return Date & Time</div>
            <div class="text-lg text-green-600 font-medium">{formatDateTime(bookingConfirmation.return_datetime)}</div>
          </div>
        </div>
      </div>
      
      <div class="mt-6 grid grid-cols-1 md:grid-cols-2 gap-6">
        <div class="bg-white p-4 rounded-lg border">
          <div class="text-sm font-medium text-gray-500 mb-1">Reason for Usage</div>
          <div class="text-gray-900">{bookingConfirmation.reason}</div>
        </div>
        
        <div class="bg-white p-4 rounded-lg border">
          <div class="text-sm font-medium text-gray-500 mb-1">Estimated Mileage</div>
          <div class="text-lg font-semibold text-gray-900">{bookingConfirmation.estimated_mileage} miles</div>
        </div>
      </div>
    </div>
    
    <div class="flex justify-center">
      <button class="btn-secondary" on:click={startNewBooking}>
        <svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"></path>
        </svg>
        Make Another Booking
      </button>
    </div>
  </div>
{:else}
  <!-- Booking Form -->
  <div class="card max-w-4xl mx-auto">
    <div class="text-center mb-8">
      <div class="bg-primary-100 rounded-full p-4 w-16 h-16 mx-auto mb-4">
        <svg class="w-8 h-8 text-primary-600 mx-auto" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path>
        </svg>
      </div>
      <h1 class="text-3xl font-bold text-gray-900 mb-2">Vehicle Booking Request</h1>
      <p class="text-lg text-gray-600">Complete the form below to request a company vehicle.</p>
    </div>

    <form on:submit={handleSubmit} class="space-y-8">
      <!-- Vehicle Selection -->
      <div class="bg-gray-50 rounded-lg p-6 border">
        <h2 class="text-xl font-semibold text-gray-900 mb-4 flex items-center">
          <svg class="w-5 h-5 text-primary-600 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"></path>
          </svg>
          Step 1: Select Vehicle
        </h2>
        <VehicleSelector
          bind:selectedVehicleId
          startDate={startDateTime ? new Date(startDateTime).toISOString().split('T')[0] : ''}
          endDate={endDateTime ? new Date(endDateTime).toISOString().split('T')[0] : ''}
          disabled={isSubmitting}
          on:vehicleSelected={handleVehicleSelected}
        />
        
        <!-- Selected Vehicle Details -->
        {#if selectedVehicle}
          <div class="mt-4 p-4 bg-primary-50 border border-primary-200 rounded-lg">
            <h3 class="text-lg font-medium text-primary-900 mb-3 flex items-center">
              <svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path>
              </svg>
              Selected Vehicle
            </h3>
            <div class="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
              <div>
                <span class="font-medium text-gray-700">Registration:</span>
                <span class="block text-gray-900 font-semibold">{selectedVehicle.registration}</span>
              </div>
              <div>
                <span class="font-medium text-gray-700">Make:</span>
                <span class="block text-gray-900">{selectedVehicle.make}</span>
              </div>
              <div>
                <span class="font-medium text-gray-700">Color:</span>
                <span class="block text-gray-900">{selectedVehicle.color}</span>
              </div>
            </div>
          </div>
        {/if}
      </div>

      <!-- Date and Time Selection -->
      <div class="bg-gray-50 rounded-lg p-6 border">
        <h2 class="text-xl font-semibold text-gray-900 mb-4 flex items-center">
          <svg class="w-5 h-5 text-primary-600 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3a2 2 0 012-2h4a2 2 0 012 2v4m-6 0V7a2 2 0 012-2h4a2 2 0 012 2v4m-6 0h8m-8 0l-2 9a1 1 0 001 1h8a1 1 0 001-1l-2-9m-8 0V7a2 2 0 012-2h4a2 2 0 012 2v4"></path>
          </svg>
          Step 2: Choose Date & Time
        </h2>
        <DateTimePicker
          bind:startDateTime
          bind:duration
          disabled={isSubmitting}
          on:dateTimeChanged={handleDateTimeChanged}
        />
      </div>

      <!-- Reason for Usage -->
      <div class="bg-gray-50 rounded-lg p-6 border">
        <h2 class="text-xl font-semibold text-gray-900 mb-4 flex items-center">
          <svg class="w-5 h-5 text-primary-600 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path>
          </svg>
          Step 3: Reason for Usage
        </h2>
        <div class="space-y-2">
          <label for="reason" class="block text-sm font-medium text-gray-700">
            Reason for Usage <span class="text-red-500">*</span>
          </label>
          <textarea
            id="reason"
            bind:value={reason}
            placeholder="Please describe the purpose of your vehicle usage..."
            disabled={isSubmitting}
            class="form-input-custom resize-none {showValidationErrors && formErrors.some(e => e.includes('reason') || e.includes('Reason')) ? 'border-red-300 focus:border-red-500 focus:ring-red-500' : ''}"
            rows="4"
            maxlength="500"
            aria-describedby="reason-help"
          ></textarea>
          <div id="reason-help" class="flex justify-between items-center text-sm">
            {#if reason}
              <span class="text-gray-500">
                {reason.length}/500 characters
              </span>
              {#if reason.length > 450}
                <span class="text-amber-600 font-medium">Character limit approaching</span>
              {/if}
            {:else}
              <span class="text-gray-500">Describe the purpose of your vehicle usage (max 500 characters)</span>
            {/if}
          </div>
        </div>
      </div>

      <!-- Estimated Mileage -->
      <div class="bg-gray-50 rounded-lg p-6 border">
        <h2 class="text-xl font-semibold text-gray-900 mb-4 flex items-center">
          <svg class="w-5 h-5 text-primary-600 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z"></path>
          </svg>
          Step 4: Estimated Mileage
        </h2>
        <div class="space-y-2">
          <label for="estimated-mileage" class="block text-sm font-medium text-gray-700">
            Estimated Mileage <span class="text-red-500">*</span>
          </label>
          <div class="relative">
            <input
              id="estimated-mileage"
              type="number"
              bind:value={estimatedMileage}
              placeholder="Enter estimated miles"
              min="1"
              max="10000"
              step="1"
              disabled={isSubmitting}
              class="form-input-custom pr-16 {showValidationErrors && formErrors.some(e => e.includes('mileage') || e.includes('Mileage')) ? 'border-red-300 focus:border-red-500 focus:ring-red-500' : ''}"
              aria-describedby="mileage-help"
            />
            <div class="absolute inset-y-0 right-0 flex items-center pr-3 pointer-events-none">
              <span class="text-gray-500 text-sm">miles</span>
            </div>
          </div>
          <div id="mileage-help" class="text-sm text-gray-500">
            Enter the estimated miles for your trip (1-10,000 miles)
          </div>
        </div>
      </div>

      <!-- Form Errors -->
      {#if showValidationErrors && formErrors.length > 0}
        <div class="bg-red-50 border border-red-200 rounded-lg p-4" role="alert" aria-live="polite">
          <div class="flex items-center mb-3">
            <svg class="w-5 h-5 text-red-400 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
            </svg>
            <h3 class="text-sm font-medium text-red-800">Please correct the following errors:</h3>
          </div>
          <div class="space-y-2">
            {#each formErrors as error}
              <div class="flex items-start">
                <svg class="w-4 h-4 text-red-400 mr-2 mt-0.5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
                </svg>
                <span class="text-sm text-red-700">{error}</span>
              </div>
            {/each}
          </div>
        </div>
      {/if}

      <!-- Submit Button -->
      <div class="flex justify-center pt-6">
        <button
          type="submit"
          disabled={!isFormValid || isSubmitting}
          class="btn-primary disabled:opacity-50 disabled:cursor-not-allowed min-w-[200px] flex items-center justify-center space-x-2 {isSubmitting ? 'cursor-wait' : ''}"
        >
          {#if isSubmitting}
            <svg class="animate-spin -ml-1 mr-3 h-5 w-5 text-white" fill="none" viewBox="0 0 24 24">
              <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
              <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
            <span>Submitting Request...</span>
          {:else}
            <svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8"></path>
            </svg>
            <span>Submit Booking Request</span>
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

  .field-help {
    margin-top: 0.25rem;
    font-size: 0.75rem;
    color: #6b7280;
  }

  .field-hint {
    color: #6b7280;
  }

  .char-count {
    color: #6b7280;
    font-weight: 500;
  }

  .char-count.warning {
    color: #f59e0b;
  }

  .form-errors {
    margin: -0.5rem 0 0 0;
    padding: 1rem;
    background-color: #fef2f2;
    border: 1px solid #fecaca;
    border-radius: 0.5rem;
    border-left: 4px solid #ef4444;
  }

  .form-errors-header h3 {
    margin: 0 0 0.75rem 0;
    color: #991b1b;
    font-size: 0.875rem;
    font-weight: 600;
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

  .vehicle-details {
    text-align: right;
  }

  .vehicle-registration {
    font-weight: 600;
    color: #1f2937;
  }

  .vehicle-info {
    font-size: 0.875rem;
    color: #6b7280;
    margin-top: 0.125rem;
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