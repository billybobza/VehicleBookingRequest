<script lang="ts">
  import { onMount } from 'svelte';
  import { adminApiService, type Booking } from '../../services/adminApi';
  
  let bookings: Booking[] = [];
  let loading = true;
  let error = '';
  let statusFilter = '';
  let vehicleFilter = '';
  
  const statusOptions = [
    { value: '', label: 'All Statuses' },
    { value: 'pending', label: 'Pending' },
    { value: 'confirmed', label: 'Confirmed' },
    { value: 'cancelled', label: 'Cancelled' },
    { value: 'completed', label: 'Completed' }
  ];
  
  onMount(async () => {
    await loadBookings();
  });
  
  async function loadBookings() {
    loading = true;
    error = '';
    
    try {
      const vehicleId = vehicleFilter ? parseInt(vehicleFilter) : undefined;
      const result = await adminApiService.getAllBookings(statusFilter || undefined, vehicleId);
      
      if (result.error) {
        error = result.error.message;
      } else {
        bookings = result.data || [];
      }
    } catch (err) {
      error = 'Failed to load bookings';
    } finally {
      loading = false;
    }
  }
  
  async function updateBookingStatus(booking: Booking, newStatus: string) {
    if (!confirm(`Change booking status to "${newStatus}"?`)) {
      return;
    }
    
    try {
      const result = await adminApiService.updateBookingStatus(booking.id, newStatus);
      if (result.error) {
        alert(`Error: ${result.error.message}`);
      } else {
        await loadBookings();
      }
    } catch (err) {
      alert('Failed to update booking status');
    }
  }
  
  async function deleteBooking(booking: Booking) {
    if (!confirm(`Are you sure you want to delete booking #${booking.id}?`)) {
      return;
    }
    
    try {
      const result = await adminApiService.deleteBooking(booking.id);
      if (result.error) {
        alert(`Error: ${result.error.message}`);
      } else {
        await loadBookings();
      }
    } catch (err) {
      alert('Failed to delete booking');
    }
  }
  
  function formatDateTime(isoString: string): string {
    return new Date(isoString).toLocaleString('en-US', {
      weekday: 'short',
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  }
  
  function getStatusColor(status: string): string {
    switch (status) {
      case 'confirmed': return 'status-confirmed';
      case 'pending': return 'status-pending';
      case 'cancelled': return 'status-cancelled';
      case 'completed': return 'status-completed';
      default: return 'status-default';
    }
  }
  
  function getStatusIcon(status: string): string {
    switch (status) {
      case 'confirmed': return '✅';
      case 'pending': return '⏳';
      case 'cancelled': return '❌';
      case 'completed': return '🏁';
      default: return '❓';
    }
  }
  
  // Reactive statement to reload bookings when filters change
  $: if (statusFilter !== undefined || vehicleFilter !== undefined) {
    loadBookings();
  }
</script>

<div class="booking-management">
  <div class="header">
    <h2>📅 Booking Management</h2>
    <button class="btn btn-primary" on:click={loadBookings}>
      🔄 Refresh
    </button>
  </div>
  
  <div class="filters">
    <div class="filter-group">
      <label for="statusFilter">Filter by Status:</label>
      <select id="statusFilter" bind:value={statusFilter}>
        {#each statusOptions as option}
          <option value={option.value}>{option.label}</option>
        {/each}
      </select>
    </div>
    
    <div class="filter-group">
      <label for="vehicleFilter">Filter by Vehicle ID:</label>
      <input
        id="vehicleFilter"
        type="number"
        bind:value={vehicleFilter}
        placeholder="Enter vehicle ID"
        min="1"
      />
    </div>
    
    <button class="btn btn-secondary" on:click={() => { statusFilter = ''; vehicleFilter = ''; }}>
      Clear Filters
    </button>
  </div>
  
  {#if loading}
    <div class="loading">Loading bookings...</div>
  {:else if error}
    <div class="error">
      <p>❌ {error}</p>
      <button on:click={loadBookings}>Try Again</button>
    </div>
  {:else}
    <div class="bookings-container">
      {#if bookings.length === 0}
        <div class="no-bookings">
          <p>No bookings found matching the current filters.</p>
        </div>
      {:else}
        <div class="bookings-table">
          <div class="table-header">
            <div class="col-id">ID</div>
            <div class="col-vehicle">Vehicle</div>
            <div class="col-dates">Booking Period</div>
            <div class="col-reason">Reason</div>
            <div class="col-mileage">Mileage</div>
            <div class="col-status">Status</div>
            <div class="col-actions">Actions</div>
          </div>
          
          {#each bookings as booking}
            <div class="table-row">
              <div class="col-id">#{booking.id}</div>
              <div class="col-vehicle">
                <div class="vehicle-info">
                  <strong>{booking.vehicle.registration}</strong>
                  <small>{booking.vehicle.make} ({booking.vehicle.color})</small>
                </div>
              </div>
              <div class="col-dates">
                <div class="date-info">
                  <div><strong>Start:</strong> {formatDateTime(booking.start_datetime)}</div>
                  <div><strong>End:</strong> {formatDateTime(booking.end_datetime)}</div>
                  <div><strong>Return:</strong> {formatDateTime(booking.return_datetime)}</div>
                </div>
              </div>
              <div class="col-reason">
                <div class="reason-text" title={booking.reason}>
                  {booking.reason.length > 50 ? booking.reason.substring(0, 50) + '...' : booking.reason}
                </div>
              </div>
              <div class="col-mileage">{booking.estimated_mileage} mi</div>
              <div class="col-status">
                <span class="status-badge {getStatusColor(booking.status)}">
                  {getStatusIcon(booking.status)} {booking.status}
                </span>
              </div>
              <div class="col-actions">
                <div class="action-buttons">
                  {#if booking.status === 'pending'}
                    <button 
                      class="btn btn-sm btn-success" 
                      on:click={() => updateBookingStatus(booking, 'confirmed')}
                    >
                      ✅ Approve
                    </button>
                  {/if}
                  
                  {#if booking.status === 'confirmed'}
                    <button 
                      class="btn btn-sm btn-warning" 
                      on:click={() => updateBookingStatus(booking, 'completed')}
                    >
                      🏁 Complete
                    </button>
                  {/if}
                  
                  {#if booking.status !== 'cancelled'}
                    <button 
                      class="btn btn-sm btn-secondary" 
                      on:click={() => updateBookingStatus(booking, 'cancelled')}
                    >
                      ❌ Cancel
                    </button>
                  {/if}
                  
                  <button 
                    class="btn btn-sm btn-danger" 
                    on:click={() => deleteBooking(booking)}
                  >
                    🗑️ Delete
                  </button>
                </div>
              </div>
            </div>
          {/each}
        </div>
      {/if}
    </div>
  {/if}
</div>

<style>
  .booking-management {
    padding: 1rem;
  }
  
  .header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 2rem;
  }
  
  .header h2 {
    margin: 0;
    color: #1f2937;
  }
  
  .filters {
    display: flex;
    gap: 1rem;
    align-items: end;
    margin-bottom: 2rem;
    padding: 1rem;
    background: #f9fafb;
    border: 1px solid #e5e7eb;
    border-radius: 0.5rem;
    flex-wrap: wrap;
  }
  
  .filter-group {
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
  }
  
  .filter-group label {
    font-size: 0.875rem;
    font-weight: 500;
    color: #374151;
  }
  
  .filter-group select,
  .filter-group input {
    padding: 0.5rem;
    border: 1px solid #d1d5db;
    border-radius: 0.375rem;
    font-size: 0.875rem;
    min-width: 150px;
  }
  
  .loading {
    text-align: center;
    padding: 3rem;
    color: #6b7280;
  }
  
  .error {
    text-align: center;
    padding: 2rem;
    background: #fef2f2;
    border: 1px solid #fecaca;
    border-radius: 0.5rem;
    color: #dc2626;
  }
  
  .no-bookings {
    text-align: center;
    padding: 3rem;
    color: #6b7280;
    background: #f9fafb;
    border: 2px dashed #d1d5db;
    border-radius: 0.5rem;
  }
  
  .bookings-table {
    background: white;
    border: 1px solid #e5e7eb;
    border-radius: 0.5rem;
    overflow: hidden;
  }
  
  .table-header {
    display: grid;
    grid-template-columns: 80px 200px 250px 1fr 100px 120px 200px;
    gap: 1rem;
    padding: 1rem;
    background: #f9fafb;
    border-bottom: 1px solid #e5e7eb;
    font-weight: 600;
    color: #374151;
    font-size: 0.875rem;
  }
  
  .table-row {
    display: grid;
    grid-template-columns: 80px 200px 250px 1fr 100px 120px 200px;
    gap: 1rem;
    padding: 1rem;
    border-bottom: 1px solid #f3f4f6;
    align-items: center;
  }
  
  .table-row:hover {
    background: #f9fafb;
  }
  
  .table-row:last-child {
    border-bottom: none;
  }
  
  .col-id {
    font-weight: 600;
    color: #6b7280;
  }
  
  .vehicle-info strong {
    display: block;
    color: #1f2937;
  }
  
  .vehicle-info small {
    color: #6b7280;
    font-size: 0.75rem;
  }
  
  .date-info {
    font-size: 0.75rem;
    line-height: 1.4;
  }
  
  .date-info div {
    margin-bottom: 0.25rem;
  }
  
  .reason-text {
    font-size: 0.875rem;
    color: #374151;
    line-height: 1.4;
  }
  
  .status-badge {
    display: inline-flex;
    align-items: center;
    gap: 0.25rem;
    padding: 0.25rem 0.75rem;
    border-radius: 9999px;
    font-size: 0.75rem;
    font-weight: 600;
    text-transform: uppercase;
  }
  
  .status-confirmed {
    background: #d1fae5;
    color: #065f46;
  }
  
  .status-pending {
    background: #fef3c7;
    color: #92400e;
  }
  
  .status-cancelled {
    background: #fee2e2;
    color: #991b1b;
  }
  
  .status-completed {
    background: #e0e7ff;
    color: #3730a3;
  }
  
  .status-default {
    background: #f3f4f6;
    color: #374151;
  }
  
  .action-buttons {
    display: flex;
    gap: 0.5rem;
    flex-wrap: wrap;
  }
  
  /* Button styles */
  .btn {
    padding: 0.5rem 1rem;
    border: none;
    border-radius: 0.375rem;
    cursor: pointer;
    font-size: 0.875rem;
    font-weight: 500;
    transition: all 0.2s;
    text-decoration: none;
    display: inline-flex;
    align-items: center;
    gap: 0.25rem;
  }
  
  .btn-sm {
    padding: 0.25rem 0.5rem;
    font-size: 0.75rem;
  }
  
  .btn-primary {
    background: #3b82f6;
    color: white;
  }
  
  .btn-primary:hover {
    background: #2563eb;
  }
  
  .btn-secondary {
    background: #6b7280;
    color: white;
  }
  
  .btn-secondary:hover {
    background: #4b5563;
  }
  
  .btn-success {
    background: #10b981;
    color: white;
  }
  
  .btn-success:hover {
    background: #059669;
  }
  
  .btn-warning {
    background: #f59e0b;
    color: white;
  }
  
  .btn-warning:hover {
    background: #d97706;
  }
  
  .btn-danger {
    background: #ef4444;
    color: white;
  }
  
  .btn-danger:hover {
    background: #dc2626;
  }
  
  /* Responsive design */
  @media (max-width: 1200px) {
    .table-header,
    .table-row {
      grid-template-columns: 60px 150px 200px 1fr 80px 100px 150px;
      font-size: 0.75rem;
    }
    
    .action-buttons {
      flex-direction: column;
    }
  }
  
  @media (max-width: 768px) {
    .filters {
      flex-direction: column;
      align-items: stretch;
    }
    
    .filter-group {
      flex-direction: row;
      align-items: center;
      justify-content: space-between;
    }
    
    .filter-group select,
    .filter-group input {
      min-width: 120px;
    }
    
    .bookings-table {
      overflow-x: auto;
    }
    
    .table-header,
    .table-row {
      min-width: 800px;
    }
  }
</style>