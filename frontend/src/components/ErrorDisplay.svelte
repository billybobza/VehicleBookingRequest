<script lang="ts">
  import { errors, removeError } from '../stores/ui.js';
  
  function handleClose(errorId: string) {
    removeError(errorId);
  }
</script>

{#if $errors.length > 0}
  <div class="error-container">
    {#each $errors as error (error.id)}
      <div class="error-message" role="alert">
        <div class="error-content">
          <strong>{error.code}:</strong> {error.message}
          {#if error.details}
            <div class="error-details">
              {JSON.stringify(error.details)}
            </div>
          {/if}
        </div>
        <button 
          class="error-close" 
          on:click={() => handleClose(error.id)}
          aria-label="Close error message"
        >
          ×
        </button>
      </div>
    {/each}
  </div>
{/if}

<style>
  .error-container {
    position: fixed;
    top: 1rem;
    right: 1rem;
    z-index: 1000;
    max-width: 400px;
  }

  .error-message {
    background-color: #fee;
    border: 1px solid #fcc;
    border-radius: 4px;
    padding: 1rem;
    margin-bottom: 0.5rem;
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  }

  .error-content {
    flex: 1;
    color: #c33;
  }

  .error-details {
    font-size: 0.875rem;
    margin-top: 0.5rem;
    color: #666;
    font-family: monospace;
  }

  .error-close {
    background: none;
    border: none;
    font-size: 1.5rem;
    color: #c33;
    cursor: pointer;
    padding: 0;
    margin-left: 1rem;
    line-height: 1;
  }

  .error-close:hover {
    color: #a11;
  }
</style>