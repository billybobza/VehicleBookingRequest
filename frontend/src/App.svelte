<script lang="ts">
  import BookingForm from './components/BookingForm.svelte';
  import ErrorDisplay from './components/ErrorDisplay.svelte';
</script>

<main>
  <ErrorDisplay />
  <BookingForm />
</main>

<style>
  main {
    min-height: 100vh;
    padding: 1rem;
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
</style>