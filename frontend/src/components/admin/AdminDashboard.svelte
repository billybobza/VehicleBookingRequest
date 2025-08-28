<script lang="ts">
  import { onMount } from 'svelte';
  import { adminApiService } from '../../services/adminApi';
  
  interface DashboardStats {
    total_vehicles: number;
    total_bookings: number;
    active_bookings: number;
    pending_bookings: number;
    offline_vehicles: number;
    available_vehicles: number;
  }
  
  let stats: DashboardStats | null = null;
  let loading = true;
  let error = '';
  
  onMount(async () => {
    await loadStats();
  });
  
  async function loadStats() {
    loading = true;
    error = '';
    
    try {
      const result = await adminApiService.getDashboardStats();
      if (result.error) {
        error = result.error.message;
      } else {
        stats = result.data;
      }
    } catch (err) {
      error = 'Failed to load dashboard statistics';
    } finally {
      loading = false;
    }
  }
</script>

<div class="dashboard">
  <div class="dashboard-header">
    <h2>📊 System Overview</h2>
    <button class="refresh-btn" on:click={loadStats} disabled={loading}>
      {loading ? '🔄' : '↻'} Refresh
    </button>
  </div>
  
  {#if loading}
    <div class="loading">Loading dashboard statistics...</div>
  {:else if error}
    <div class="error">
      <p>❌ {error}</p>
      <button on:click={loadStats}>Try Again</button>
    </div>
  {:else if stats}
    <div class="stats-grid">
      <div class="stat-card vehicles">
        <div class="stat-icon">🚗</div>
        <div class="stat-content">
          <h3>Total Vehicles</h3>
          <div class="stat-number">{stats.total_vehicles}</div>
          <div class="stat-detail">
            <span class="available">{stats.available_vehicles} available</span>
            <span class="offline">{stats.offline_vehicles} offline</span>
          </div>
        </div>
      </div>
      
      <div class="stat-card bookings">
        <div class="stat-icon">📅</div>
        <div class="stat-content">
          <h3>Total Bookings</h3>
          <div class="stat-number">{stats.total_bookings}</div>
          <div class="stat-detail">All time bookings</div>
        </div>
      </div>
      
      <div class="stat-card active">
        <div class="stat-icon">✅</div>
        <div class="stat-content">
          <h3>Active Bookings</h3>
          <div class="stat-number">{stats.active_bookings}</div>
          <div class="stat-detail">Currently confirmed</div>
        </div>
      </div>
      
      <div class="stat-card pending">
        <div class="stat-icon">⏳</div>
        <div class="stat-content">
          <h3>Pending Bookings</h3>
          <div class="stat-number">{stats.pending_bookings}</div>
          <div class="stat-detail">Awaiting approval</div>
        </div>
      </div>
    </div>
    
    <div class="quick-actions">
      <h3>Quick Actions</h3>
      <div class="action-buttons">
        <button class="action-btn add-vehicle">
          <span class="action-icon">➕</span>
          Add New Vehicle
        </button>
        <button class="action-btn manage-bookings">
          <span class="action-icon">📋</span>
          Manage Bookings
        </button>
        <button class="action-btn system-settings">
          <span class="action-icon">⚙️</span>
          System Settings
        </button>
      </div>
    </div>
  {/if}
</div>

<style>
  .dashboard {
    padding: 1rem;
  }
  
  .dashboard-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 2rem;
  }
  
  .dashboard-header h2 {
    color: #1f2937;
    margin: 0;
  }
  
  .refresh-btn {
    padding: 0.5rem 1rem;
    background: #3b82f6;
    color: white;
    border: none;
    border-radius: 0.375rem;
    cursor: pointer;
    font-size: 0.875rem;
    transition: background-color 0.2s;
  }
  
  .refresh-btn:hover:not(:disabled) {
    background: #2563eb;
  }
  
  .refresh-btn:disabled {
    opacity: 0.6;
    cursor: not-allowed;
  }
  
  .loading {
    text-align: center;
    padding: 3rem;
    color: #6b7280;
    font-size: 1.1rem;
  }
  
  .error {
    text-align: center;
    padding: 2rem;
    background: #fef2f2;
    border: 1px solid #fecaca;
    border-radius: 0.5rem;
    color: #dc2626;
  }
  
  .error button {
    margin-top: 1rem;
    padding: 0.5rem 1rem;
    background: #dc2626;
    color: white;
    border: none;
    border-radius: 0.375rem;
    cursor: pointer;
  }
  
  .stats-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
    gap: 1.5rem;
    margin-bottom: 2rem;
  }
  
  .stat-card {
    background: white;
    border: 1px solid #e5e7eb;
    border-radius: 0.5rem;
    padding: 1.5rem;
    display: flex;
    align-items: center;
    gap: 1rem;
    transition: transform 0.2s, box-shadow 0.2s;
  }
  
  .stat-card:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  }
  
  .stat-card.vehicles {
    border-left: 4px solid #3b82f6;
  }
  
  .stat-card.bookings {
    border-left: 4px solid #10b981;
  }
  
  .stat-card.active {
    border-left: 4px solid #f59e0b;
  }
  
  .stat-card.pending {
    border-left: 4px solid #ef4444;
  }
  
  .stat-icon {
    font-size: 2rem;
    opacity: 0.8;
  }
  
  .stat-content h3 {
    margin: 0 0 0.5rem 0;
    color: #374151;
    font-size: 0.875rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.05em;
  }
  
  .stat-number {
    font-size: 2rem;
    font-weight: 700;
    color: #1f2937;
    margin-bottom: 0.25rem;
  }
  
  .stat-detail {
    font-size: 0.75rem;
    color: #6b7280;
    display: flex;
    gap: 0.5rem;
  }
  
  .available {
    color: #10b981;
  }
  
  .offline {
    color: #ef4444;
  }
  
  .quick-actions {
    background: #f9fafb;
    border: 1px solid #e5e7eb;
    border-radius: 0.5rem;
    padding: 1.5rem;
  }
  
  .quick-actions h3 {
    margin: 0 0 1rem 0;
    color: #374151;
  }
  
  .action-buttons {
    display: flex;
    gap: 1rem;
    flex-wrap: wrap;
  }
  
  .action-btn {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    padding: 0.75rem 1rem;
    background: white;
    border: 1px solid #d1d5db;
    border-radius: 0.375rem;
    cursor: pointer;
    font-size: 0.875rem;
    color: #374151;
    transition: all 0.2s;
  }
  
  .action-btn:hover {
    background: #f3f4f6;
    border-color: #9ca3af;
    transform: translateY(-1px);
  }
  
  .action-icon {
    font-size: 1rem;
  }
</style>