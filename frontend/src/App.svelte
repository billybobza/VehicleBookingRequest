<script lang="ts">
  import BookingForm from './components/BookingForm.svelte';
  import AdminPage from './components/AdminPage.svelte';
  import ErrorDisplay from './components/ErrorDisplay.svelte';
  import SuccessDisplay from './components/SuccessDisplay.svelte';
  import { globalLoading } from './stores/ui';
  
  let currentPage = 'booking';
  
  // Simple routing
  function navigateTo(page: string) {
    currentPage = page;
  }
</script>

<div class="app">
  <nav class="navbar" role="navigation" aria-label="Main navigation">
    <div class="nav-container">
      <div class="nav-brand">
        <h1>🚗 Car Booking System</h1>
      </div>
      
      <div class="nav-links" role="tablist">
        <button 
          class="nav-link {currentPage === 'booking' ? 'active' : ''}"
          on:click={() => navigateTo('booking')}
          role="tab"
          aria-selected={currentPage === 'booking'}
          aria-controls="main-content"
          disabled={$globalLoading}
        >
          <span aria-hidden="true">📅</span> Book Vehicle
        </button>
        <button 
          class="nav-link {currentPage === 'admin' ? 'active' : ''}"
          on:click={() => navigateTo('admin')}
          role="tab"
          aria-selected={currentPage === 'admin'}
          aria-controls="main-content"
          disabled={$globalLoading}
        >
          <span aria-hidden="true">🔧</span> Admin Panel
        </button>
      </div>
    </div>
  </nav>
  
  <main id="main-content" role="main" aria-live="polite">
    <ErrorDisplay />
    <SuccessDisplay />
    
    {#if $globalLoading}
      <div class="global-loading-overlay" aria-label="Loading application">
        <div class="global-loading-content">
          <div class="loading-spinner"></div>
          <p>Loading...</p>
        </div>
      </div>
    {/if}
    
    {#if currentPage === 'booking'}
      <BookingForm />
    {:else if currentPage === 'admin'}
      <AdminPage />
    {/if}
  </main>
</div>

<style>
  .app {
    min-height: 100vh;
    display: flex;
    flex-direction: column;
  }
  
  .navbar {
    background: white;
    border-bottom: 1px solid #e5e7eb;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  }
  
  .nav-container {
    max-width: 1200px;
    margin: 0 auto;
    padding: 1rem 2rem;
    display: flex;
    justify-content: space-between;
    align-items: center;
  }
  
  .nav-brand h1 {
    margin: 0;
    color: #2563eb;
    font-size: 1.5rem;
  }
  
  .nav-links {
    display: flex;
    gap: 1rem;
  }
  
  .nav-link {
    padding: 0.75rem 1.5rem;
    background: none;
    border: 1px solid #e5e7eb;
    border-radius: 0.5rem;
    cursor: pointer;
    font-size: 1rem;
    color: #374151;
    transition: all 0.2s ease;
    display: flex;
    align-items: center;
    gap: 0.5rem;
  }
  
  .nav-link:hover:not(:disabled) {
    background: #f3f4f6;
    border-color: #d1d5db;
  }

  .nav-link:focus {
    outline: 2px solid #3b82f6;
    outline-offset: 2px;
  }
  
  .nav-link.active {
    background: #2563eb;
    color: white;
    border-color: #2563eb;
  }

  .nav-link:disabled {
    opacity: 0.6;
    cursor: not-allowed;
  }
  
  main {
    flex: 1;
    padding: 2rem;
    background-color: #f5f5f5;
    position: relative;
  }

  .global-loading-overlay {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background-color: rgba(255, 255, 255, 0.9);
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 9999;
    backdrop-filter: blur(2px);
  }

  .global-loading-content {
    text-align: center;
    padding: 2rem;
    background: white;
    border-radius: 0.5rem;
    box-shadow: 0 10px 25px rgba(0, 0, 0, 0.1);
  }

  .loading-spinner {
    width: 40px;
    height: 40px;
    border: 4px solid #e5e7eb;
    border-top: 4px solid #3b82f6;
    border-radius: 50%;
    animation: spin 1s linear infinite;
    margin: 0 auto 1rem;
  }

  .global-loading-content p {
    margin: 0;
    color: #6b7280;
    font-weight: 500;
  }

  @keyframes spin {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
  }

  :global(body) {
    margin: 0;
    padding: 0;
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    background-color: #f5f5f5;
  }

  :global(*) {
    box-sizing: border-box;
  }
  
  @media (max-width: 768px) {
    .nav-container {
      flex-direction: column;
      gap: 1rem;
      padding: 1rem;
    }
    
    .nav-links {
      width: 100%;
      justify-content: center;
    }
    
    main {
      padding: 1rem;
    }
  }
</style>