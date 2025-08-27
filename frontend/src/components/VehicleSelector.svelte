<script lang="ts">
  import { onMount } from 'svelte';
  import { apiService, type Vehicle, type AvailableVehicle } from '../services/api';
  import LoadingSpinner from './LoadingSpinner.svelte';
  import ErrorMessage from './ErrorMessage.svelte';

  // Props
  export let selectedVehicleId: number | null = null;
  export let startDate: string = '';
  export let endDate: string = '';
  export let disabled: boolean = false;

  // State
  let vehicles: Vehicle[] = [];
  let availableVehicles: AvailableVehicle[] = [];
  let loading = false;
  let error: string | null = null;
  let showAvailableOnly = false;

  // Reactive statements
  $: displayVehicles = showAvailableOnly ? availableVehicles : vehicles;
  $: canShowAvailable = startDate && endDate;

  // Event dispatcher
  import { createEventDispatcher } from 'svelte';
  const dispatch = createEventDispatcher<{
    vehicleSelected: { vehicleId: number; vehicle: Vehicle };
  }>();

  // Load all vehicles on mount
  onMount(async () => {
    await loadVehicles();
  });

  // Watch for date changes to update available vehicles
  $: if (canShowAvailable && showAvailableOnly) {
    loadAvailableVehicles();
  }

  // Watch for vehicle selection changes
  $: if (selectedVehicleId) {
    const selectedVehicle = displayVehicles.find(v => v.id === selectedVehicleId);
    if (selectedVehicle) {
      dispatch('vehicleSelected', { vehicleId: selectedVehicleId, vehicle: selectedVehicle });
    }
  }

  async function loadVehicles() {
    loading = true;
    error = null;

    const response = await apiService.getVehicles();
    
    if (response.error) {
      error = response.error.message;
    } else if (response.data) {
      vehicles = response.data;
    }

    loading = false;
  }

  async function loadAvailableVehicles() {
    if (!startDate || !endDate) return;

    loading = true;
    error = null;

    const response = await apiService.getAvailableVehicles(startDate, endDate);
    
    if (response.error) {
      error = response.error.message;
      showAvailableOnly = false; // Fall back to showing all vehicles
    } else if (response.data) {
      availableVehicles = response.data;
    }

    loading = false;
  }


  function toggleAvailableOnly() {
    showAvailableOnly = !showAvailableOnly;
    if (showAvailableOnly && canShowAvailable) {
      loadAvailableVehicles();
    }
    // Reset selection when switching modes
    selectedVehicleId = null;
  }

  function formatVehicleDisplay(vehicle: Vehicle): string {
    return `${vehicle.registration} - ${vehicle.make} (${vehicle.color})`;
  }
</script>

<div class="vehicle-selector">
  <div class="selector-header">
    <label for="vehicle-select" class="vehicle-label">
      Select Vehicle <span class="required">*</span>
    </label>
    
    {#if canShowAvailable}
      <label class="availability-toggle">
        <input
          type="checkbox"
          bind:checked={showAvailableOnly}
          on:change={toggleAvailableOnly}
          {disabled}
        />
        Show available only
      </label>
    {/if}
  </div>

  <div class="select-container">
    <select
      id="vehicle-select"
      bind:value={selectedVehicleId}
      {disabled}
      class:loading
    >
      <option value="">
        {loading ? 'Loading vehicles...' : 'Choose a vehicle'}
      </option>
      
      {#each displayVehicles as vehicle (vehicle.id)}
        <option value={vehicle.id}>
          {formatVehicleDisplay(vehicle)}
        </option>
      {/each}
    </select>

    {#if loading}
      <div class="loading-indicator">
        <LoadingSpinner size="small" />
      </div>
    {/if}
  </div>

  {#if error}
    <ErrorMessage message={error} />
  {/if}

  {#if showAvailableOnly && availableVehicles.length === 0 && !loading && !error}
    <div class="no-vehicles">
      No vehicles available for the selected dates. Try different dates or show all vehicles.
    </div>
  {/if}

  {#if displayVehicles.length === 0 && !loading && !error}
    <div class="no-vehicles">
      No vehicles found. Please contact your administrator.
    </div>
  {/if}
</div>

<style>
  .vehicle-selector {
    margin-bottom: 1rem;
  }

  .selector-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 0.5rem;
  }

  .vehicle-label {
    font-weight: 600;
    color: #374151;
    font-size: 0.875rem;
  }

  .required {
    color: #ef4444;
  }

  .availability-toggle {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    font-size: 0.875rem;
    color: #6b7280;
    cursor: pointer;
  }

  .availability-toggle input[type="checkbox"] {
    cursor: pointer;
  }

  .select-container {
    position: relative;
  }

  select {
    width: 100%;
    padding: 0.75rem;
    border: 1px solid #d1d5db;
    border-radius: 0.375rem;
    font-size: 1rem;
    background-color: white;
    cursor: pointer;
    transition: border-color 0.2s, box-shadow 0.2s;
  }

  select:focus {
    outline: none;
    border-color: #3b82f6;
    box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
  }

  select:disabled {
    background-color: #f9fafb;
    color: #6b7280;
    cursor: not-allowed;
  }

  select.loading {
    color: #6b7280;
  }

  .loading-indicator {
    position: absolute;
    right: 0.75rem;
    top: 50%;
    transform: translateY(-50%);
    pointer-events: none;
  }

  .no-vehicles {
    margin-top: 0.5rem;
    padding: 0.75rem;
    background-color: #fef3c7;
    border: 1px solid #f59e0b;
    border-radius: 0.375rem;
    color: #92400e;
    font-size: 0.875rem;
  }

  /* Responsive design */
  @media (max-width: 640px) {
    .selector-header {
      flex-direction: column;
      align-items: flex-start;
      gap: 0.5rem;
    }
  }
</style>