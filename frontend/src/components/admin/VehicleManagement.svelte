<script lang="ts">
  import { onMount } from 'svelte';
  import { adminApiService, type Vehicle, type VehicleCreate, type VehicleUpdate } from '../../services/adminApi';
  
  let vehicles: Vehicle[] = [];
  let loading = true;
  let error = '';
  let showAddForm = false;
  let editingVehicle: Vehicle | null = null;
  
  // Form data
  let formData: VehicleCreate = {
    registration: '',
    make: '',
    color: ''
  };
  
  // Offline management
  let showOfflineForm = false;
  let offlineVehicleId: number | null = null;
  let offlineData = {
    startDate: '',
    endDate: '',
    reason: ''
  };
  
  onMount(async () => {
    await loadVehicles();
  });
  
  async function loadVehicles() {
    loading = true;
    error = '';
    
    try {
      const result = await adminApiService.getAllVehicles();
      if (result.error) {
        error = result.error.message;
      } else {
        vehicles = result.data || [];
      }
    } catch (err) {
      error = 'Failed to load vehicles';
    } finally {
      loading = false;
    }
  }
  
  function showAddVehicleForm() {
    formData = { registration: '', make: '', color: '' };
    editingVehicle = null;
    showAddForm = true;
  }
  
  function showEditVehicleForm(vehicle: Vehicle) {
    formData = {
      registration: vehicle.registration,
      make: vehicle.make,
      color: vehicle.color
    };
    editingVehicle = vehicle;
    showAddForm = true;
  }
  
  function cancelForm() {
    showAddForm = false;
    editingVehicle = null;
    formData = { registration: '', make: '', color: '' };
  }
  
  async function saveVehicle() {
    if (!formData.registration || !formData.make || !formData.color) {
      alert('Please fill in all fields');
      return;
    }
    
    try {
      let result;
      if (editingVehicle) {
        result = await adminApiService.updateVehicle(editingVehicle.id, formData);
      } else {
        result = await adminApiService.createVehicle(formData);
      }
      
      if (result.error) {
        alert(`Error: ${result.error.message}`);
      } else {
        await loadVehicles();
        cancelForm();
      }
    } catch (err) {
      alert('Failed to save vehicle');
    }
  }
  
  async function deleteVehicle(vehicle: Vehicle) {
    if (!confirm(`Are you sure you want to delete vehicle ${vehicle.registration}?`)) {
      return;
    }
    
    try {
      const result = await adminApiService.deleteVehicle(vehicle.id);
      if (result.error) {
        alert(`Error: ${result.error.message}`);
      } else {
        await loadVehicles();
      }
    } catch (err) {
      alert('Failed to delete vehicle');
    }
  }
  
  function showTakeOfflineForm(vehicle: Vehicle) {
    offlineVehicleId = vehicle.id;
    offlineData = { startDate: '', endDate: '', reason: '' };
    showOfflineForm = true;
  }
  
  function cancelOfflineForm() {
    showOfflineForm = false;
    offlineVehicleId = null;
    offlineData = { startDate: '', endDate: '', reason: '' };
  }
  
  async function takeVehicleOffline() {
    if (!offlineData.startDate || !offlineData.endDate || !offlineData.reason) {
      alert('Please fill in all fields');
      return;
    }
    
    if (offlineVehicleId === null) return;
    
    try {
      const result = await adminApiService.takeVehicleOffline(
        offlineVehicleId,
        offlineData.startDate,
        offlineData.endDate,
        offlineData.reason
      );
      
      if (result.error) {
        alert(`Error: ${result.error.message}`);
      } else {
        alert('Vehicle taken offline successfully');
        await loadVehicles();
        cancelOfflineForm();
      }
    } catch (err) {
      alert('Failed to take vehicle offline');
    }
  }
  
  async function bringVehicleOnline(vehicle: Vehicle) {
    if (!confirm(`Bring vehicle ${vehicle.registration} back online?`)) {
      return;
    }
    
    try {
      const result = await adminApiService.bringVehicleOnline(vehicle.id);
      if (result.error) {
        alert(`Error: ${result.error.message}`);
      } else {
        alert('Vehicle brought back online successfully');
        await loadVehicles();
      }
    } catch (err) {
      alert('Failed to bring vehicle online');
    }
  }
</script>

<div class="vehicle-management">
  <div class="header">
    <h2>🚗 Vehicle Management</h2>
    <button class="btn btn-primary" on:click={showAddVehicleForm}>
      ➕ Add New Vehicle
    </button>
  </div>
  
  {#if loading}
    <div class="loading">Loading vehicles...</div>
  {:else if error}
    <div class="error">
      <p>❌ {error}</p>
      <button on:click={loadVehicles}>Try Again</button>
    </div>
  {:else}
    <div class="vehicles-grid">
      {#each vehicles as vehicle}
        <div class="vehicle-card">
          <div class="vehicle-header">
            <h3>{vehicle.registration}</h3>
            <div class="vehicle-actions">
              <button class="btn btn-sm btn-secondary" on:click={() => showEditVehicleForm(vehicle)}>
                ✏️ Edit
              </button>
              <button class="btn btn-sm btn-warning" on:click={() => showTakeOfflineForm(vehicle)}>
                🔧 Offline
              </button>
              <button class="btn btn-sm btn-success" on:click={() => bringVehicleOnline(vehicle)}>
                ✅ Online
              </button>
              <button class="btn btn-sm btn-danger" on:click={() => deleteVehicle(vehicle)}>
                🗑️ Delete
              </button>
            </div>
          </div>
          
          <div class="vehicle-details">
            <p><strong>Make:</strong> {vehicle.make}</p>
            <p><strong>Color:</strong> {vehicle.color}</p>
            <p><strong>Added:</strong> {new Date(vehicle.created_at).toLocaleDateString()}</p>
          </div>
        </div>
      {/each}
      
      {#if vehicles.length === 0}
        <div class="no-vehicles">
          <p>No vehicles found. Add your first vehicle to get started!</p>
        </div>
      {/if}
    </div>
  {/if}
</div>

<!-- Add/Edit Vehicle Modal -->
{#if showAddForm}
  <div class="modal-overlay" on:click={cancelForm}>
    <div class="modal" on:click|stopPropagation>
      <div class="modal-header">
        <h3>{editingVehicle ? 'Edit Vehicle' : 'Add New Vehicle'}</h3>
        <button class="close-btn" on:click={cancelForm}>✕</button>
      </div>
      
      <form on:submit|preventDefault={saveVehicle}>
        <div class="form-group">
          <label for="registration">Registration Number</label>
          <input
            id="registration"
            type="text"
            bind:value={formData.registration}
            placeholder="e.g., ABC123"
            required
          />
        </div>
        
        <div class="form-group">
          <label for="make">Make/Manufacturer</label>
          <input
            id="make"
            type="text"
            bind:value={formData.make}
            placeholder="e.g., Toyota"
            required
          />
        </div>
        
        <div class="form-group">
          <label for="color">Color</label>
          <input
            id="color"
            type="text"
            bind:value={formData.color}
            placeholder="e.g., Blue"
            required
          />
        </div>
        
        <div class="form-actions">
          <button type="button" class="btn btn-secondary" on:click={cancelForm}>
            Cancel
          </button>
          <button type="submit" class="btn btn-primary">
            {editingVehicle ? 'Update Vehicle' : 'Add Vehicle'}
          </button>
        </div>
      </form>
    </div>
  </div>
{/if}

<!-- Take Offline Modal -->
{#if showOfflineForm}
  <div class="modal-overlay" on:click={cancelOfflineForm}>
    <div class="modal" on:click|stopPropagation>
      <div class="modal-header">
        <h3>Take Vehicle Offline</h3>
        <button class="close-btn" on:click={cancelOfflineForm}>✕</button>
      </div>
      
      <form on:submit|preventDefault={takeVehicleOffline}>
        <div class="form-group">
          <label for="startDate">Start Date</label>
          <input
            id="startDate"
            type="date"
            bind:value={offlineData.startDate}
            required
          />
        </div>
        
        <div class="form-group">
          <label for="endDate">End Date</label>
          <input
            id="endDate"
            type="date"
            bind:value={offlineData.endDate}
            required
          />
        </div>
        
        <div class="form-group">
          <label for="reason">Reason</label>
          <textarea
            id="reason"
            bind:value={offlineData.reason}
            placeholder="e.g., Scheduled maintenance, repairs, etc."
            rows="3"
            required
          ></textarea>
        </div>
        
        <div class="form-actions">
          <button type="button" class="btn btn-secondary" on:click={cancelOfflineForm}>
            Cancel
          </button>
          <button type="submit" class="btn btn-warning">
            Take Offline
          </button>
        </div>
      </form>
    </div>
  </div>
{/if}

<style>
  .vehicle-management {
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
  
  .vehicles-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
    gap: 1.5rem;
  }
  
  .vehicle-card {
    background: white;
    border: 1px solid #e5e7eb;
    border-radius: 0.5rem;
    padding: 1.5rem;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  }
  
  .vehicle-header {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    margin-bottom: 1rem;
  }
  
  .vehicle-header h3 {
    margin: 0;
    color: #1f2937;
    font-size: 1.25rem;
  }
  
  .vehicle-actions {
    display: flex;
    gap: 0.5rem;
    flex-wrap: wrap;
  }
  
  .vehicle-details p {
    margin: 0.5rem 0;
    color: #6b7280;
  }
  
  .no-vehicles {
    grid-column: 1 / -1;
    text-align: center;
    padding: 3rem;
    color: #6b7280;
    background: #f9fafb;
    border: 2px dashed #d1d5db;
    border-radius: 0.5rem;
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
  
  /* Modal styles */
  .modal-overlay {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: rgba(0, 0, 0, 0.5);
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 1000;
  }
  
  .modal {
    background: white;
    border-radius: 0.5rem;
    padding: 0;
    max-width: 500px;
    width: 90%;
    max-height: 90vh;
    overflow-y: auto;
  }
  
  .modal-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 1.5rem;
    border-bottom: 1px solid #e5e7eb;
  }
  
  .modal-header h3 {
    margin: 0;
    color: #1f2937;
  }
  
  .close-btn {
    background: none;
    border: none;
    font-size: 1.5rem;
    cursor: pointer;
    color: #6b7280;
    padding: 0;
    width: 2rem;
    height: 2rem;
    display: flex;
    align-items: center;
    justify-content: center;
  }
  
  .close-btn:hover {
    color: #374151;
  }
  
  form {
    padding: 1.5rem;
  }
  
  .form-group {
    margin-bottom: 1rem;
  }
  
  .form-group label {
    display: block;
    margin-bottom: 0.5rem;
    color: #374151;
    font-weight: 500;
  }
  
  .form-group input,
  .form-group textarea {
    width: 100%;
    padding: 0.75rem;
    border: 1px solid #d1d5db;
    border-radius: 0.375rem;
    font-size: 1rem;
    box-sizing: border-box;
  }
  
  .form-group input:focus,
  .form-group textarea:focus {
    outline: none;
    border-color: #3b82f6;
    box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
  }
  
  .form-actions {
    display: flex;
    gap: 1rem;
    justify-content: flex-end;
    margin-top: 1.5rem;
  }
</style>