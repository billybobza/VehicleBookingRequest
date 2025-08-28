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

<div class="min-h-screen bg-gray-50">
  <!-- Navigation -->
  <nav class="bg-white border-b border-gray-200 shadow-sm">
    <div class="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
      <div class="flex justify-between items-center h-16">
        <!-- Brand -->
        <div class="flex items-center space-x-3">
          <div class="bg-primary-600 rounded-lg p-2">
            <svg class="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"></path>
            </svg>
          </div>
          <h1 class="text-xl font-bold text-gray-900">Vehicle Booking System</h1>
        </div>
        
        <!-- Navigation Links -->
        <div class="flex space-x-4">
          <button 
            class="{currentPage === 'booking' 
              ? 'bg-primary-600 text-white border-primary-600' 
              : 'bg-white text-gray-700 border-gray-300 hover:bg-gray-50'} 
              inline-flex items-center px-4 py-2 border text-sm font-medium rounded-md transition-colors duration-200 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2"
            on:click={() => navigateTo('booking')}
            disabled={$globalLoading}
          >
            <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3a2 2 0 012-2h4a2 2 0 012 2v4m-6 0V7a2 2 0 012-2h4a2 2 0 012 2v4m-6 0h8m-8 0l-2 9a1 1 0 001 1h8a1 1 0 001-1l-2-9m-8 0V7a2 2 0 012-2h4a2 2 0 012 2v4"></path>
            </svg>
            Book Vehicle
          </button>
          <button 
            class="{currentPage === 'admin' 
              ? 'bg-primary-600 text-white border-primary-600' 
              : 'bg-white text-gray-700 border-gray-300 hover:bg-gray-50'} 
              inline-flex items-center px-4 py-2 border text-sm font-medium rounded-md transition-colors duration-200 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2"
            on:click={() => navigateTo('admin')}
            disabled={$globalLoading}
          >
            <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z"></path>
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"></path>
            </svg>
            Admin Panel
          </button>
        </div>
      </div>
    </div>
  </nav>
  
  <!-- Main Content -->
  <main class="container-custom">
    <ErrorDisplay />
    <SuccessDisplay />
    
    <!-- Global Loading Overlay -->
    {#if $globalLoading}
      <div class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
        <div class="bg-white rounded-lg p-8 max-w-sm mx-4 text-center">
          <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600 mx-auto mb-4"></div>
          <p class="text-gray-700 font-medium">Loading...</p>
        </div>
      </div>
    {/if}
    
    <!-- Page Content -->
    {#if currentPage === 'booking'}
      <BookingForm />
    {:else if currentPage === 'admin'}
      <AdminPage />
    {/if}
  </main>
</div>

<style>
  /* Additional custom styles for enhanced visual appeal */
  :global(.container-custom) {
    @apply max-w-6xl mx-auto px-4 py-8;
  }
  
  /* Mobile responsiveness */
  @media (max-width: 768px) {
    :global(.container-custom) {
      @apply px-4 py-6;
    }
    
    /* Mobile navigation adjustments */
    .nav-brand h1 {
      @apply text-lg;
    }
    
    .nav-links {
      @apply flex-col space-y-2 space-x-0;
    }
    
    .nav-links button {
      @apply w-full justify-center;
    }
  }
</style>