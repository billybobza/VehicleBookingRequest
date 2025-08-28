<script lang="ts">
  import { onMount } from 'svelte';
  import VehicleManagement from './admin/VehicleManagement.svelte';
  import BookingManagement from './admin/BookingManagement.svelte';
  import AdminDashboard from './admin/AdminDashboard.svelte';
  
  let activeTab = 'dashboard';
  
  const tabs = [
    { id: 'dashboard', label: 'Dashboard', icon: '📊' },
    { id: 'vehicles', label: 'Vehicle Management', icon: '🚗' },
    { id: 'bookings', label: 'Booking Management', icon: '📅' }
  ];
  
  function setActiveTab(tabId: string) {
    activeTab = tabId;
  }
</script>

<div class="admin-page">
  <div class="admin-header">
    <h1>🔧 Admin Panel</h1>
    <p>Manage vehicles, bookings, and system settings</p>
  </div>
  
  <div class="admin-tabs">
    {#each tabs as tab}
      <button 
        class="tab-button {activeTab === tab.id ? 'active' : ''}"
        on:click={() => setActiveTab(tab.id)}
      >
        <span class="tab-icon">{tab.icon}</span>
        <span class="tab-label">{tab.label}</span>
      </button>
    {/each}
  </div>
  
  <div class="admin-content">
    {#if activeTab === 'dashboard'}
      <AdminDashboard />
    {:else if activeTab === 'vehicles'}
      <VehicleManagement />
    {:else if activeTab === 'bookings'}
      <BookingManagement />
    {/if}
  </div>
</div>

<style>
  .admin-page {
    max-width: 1200px;
    margin: 0 auto;
    padding: 2rem;
  }
  
  .admin-header {
    text-align: center;
    margin-bottom: 2rem;
  }
  
  .admin-header h1 {
    color: #2563eb;
    margin-bottom: 0.5rem;
  }
  
  .admin-header p {
    color: #6b7280;
    font-size: 1.1rem;
  }
  
  .admin-tabs {
    display: flex;
    gap: 0.5rem;
    margin-bottom: 2rem;
    border-bottom: 2px solid #e5e7eb;
  }
  
  .tab-button {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    padding: 1rem 1.5rem;
    background: none;
    border: none;
    border-bottom: 3px solid transparent;
    cursor: pointer;
    font-size: 1rem;
    color: #6b7280;
    transition: all 0.2s ease;
  }
  
  .tab-button:hover {
    color: #2563eb;
    background-color: #f3f4f6;
  }
  
  .tab-button.active {
    color: #2563eb;
    border-bottom-color: #2563eb;
    background-color: #eff6ff;
  }
  
  .tab-icon {
    font-size: 1.2rem;
  }
  
  .tab-label {
    font-weight: 500;
  }
  
  .admin-content {
    background: white;
    border-radius: 0.5rem;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
    padding: 2rem;
  }
</style>