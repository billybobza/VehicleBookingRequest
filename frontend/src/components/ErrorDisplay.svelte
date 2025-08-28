<script lang="ts">
  import { errors, removeError } from '../stores/ui.js';
  import { onMount } from 'svelte';
  
  function handleClose(errorId: string) {
    removeError(errorId);
  }

  // Auto-focus on first error for screen readers
  let errorContainer: HTMLDivElement;
  
  $: if ($errors.length > 0 && errorContainer) {
    // Announce new errors to screen readers
    const firstError = errorContainer.querySelector('.error-message');
    if (firstError) {
      (firstError as HTMLElement).focus();
    }
  }
</script>

{#if $errors.length > 0}
  <div class="error-container" bind:this={errorContainer} aria-live="polite" aria-label="Error notifications">
    {#each $errors as error (error.id)}
      <div 
        class="error-message" 
        class:error-critical={error.code.includes('500') || error.code.includes('DATABASE') || error.code.includes('INTERNAL')}
        class:error-warning={error.code.includes('400') || error.code.includes('VALIDATION')}
        class:error-network={error.code.includes('NETWORK')}
        role="alert" 
        tabindex="-1"
        aria-describedby="error-{error.id}-details"
      >
        <div class="error-icon">
          {#if error.code.includes('500') || error.code.includes('DATABASE') || error.code.includes('INTERNAL')}
            ⚠️
          {:else if error.code.includes('NETWORK')}
            🌐
          {:else if error.code.includes('400') || error.code.includes('VALIDATION')}
            ℹ️
          {:else}
            ❌
          {/if}
        </div>
        <div class="error-content">
          <div class="error-title">
            {#if error.code.includes('500') || error.code.includes('DATABASE') || error.code.includes('INTERNAL')}
              Server Error
            {:else if error.code.includes('NETWORK')}
              Connection Error
            {:else if error.code.includes('400') || error.code.includes('VALIDATION')}
              Validation Error
            {:else if error.code.includes('404')}
              Not Found
            {:else}
              Error
            {/if}
          </div>
          <div class="error-message-text">{error.message}</div>
          {#if error.details && typeof error.details === 'object' && Array.isArray(error.details)}
            <div id="error-{error.id}-details" class="error-details">
              <details>
                <summary>Show details</summary>
                <ul class="error-details-list">
                  {#each error.details as detail}
                    <li>
                      {#if detail.loc && detail.msg}
                        <strong>{detail.loc[detail.loc.length - 1]}:</strong> {detail.msg}
                      {:else}
                        {JSON.stringify(detail)}
                      {/if}
                    </li>
                  {/each}
                </ul>
              </details>
            </div>
          {:else if error.details}
            <div id="error-{error.id}-details" class="error-details">
              <details>
                <summary>Show details</summary>
                <pre>{JSON.stringify(error.details, null, 2)}</pre>
              </details>
            </div>
          {/if}
        </div>
        <button 
          class="error-close" 
          on:click={() => handleClose(error.id)}
          aria-label="Close error message"
          title="Close error message"
        >
          <span aria-hidden="true">×</span>
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
    max-width: 420px;
    pointer-events: none;
  }

  .error-message {
    background-color: #fef2f2;
    border: 1px solid #fecaca;
    border-left: 4px solid #ef4444;
    border-radius: 0.5rem;
    padding: 1rem;
    margin-bottom: 0.75rem;
    display: flex;
    align-items: flex-start;
    gap: 0.75rem;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1), 0 1px 3px rgba(0, 0, 0, 0.08);
    pointer-events: auto;
    animation: slideIn 0.3s ease-out;
    transition: all 0.2s ease;
  }

  .error-message:focus {
    outline: 2px solid #3b82f6;
    outline-offset: 2px;
  }

  .error-message.error-critical {
    background-color: #fef2f2;
    border-color: #fecaca;
    border-left-color: #dc2626;
  }

  .error-message.error-warning {
    background-color: #fffbeb;
    border-color: #fed7aa;
    border-left-color: #f59e0b;
  }

  .error-message.error-network {
    background-color: #eff6ff;
    border-color: #bfdbfe;
    border-left-color: #3b82f6;
  }

  .error-icon {
    font-size: 1.25rem;
    flex-shrink: 0;
    margin-top: 0.125rem;
  }

  .error-content {
    flex: 1;
    min-width: 0;
  }

  .error-title {
    font-weight: 600;
    font-size: 0.875rem;
    color: #374151;
    margin-bottom: 0.25rem;
  }

  .error-message-text {
    color: #6b7280;
    font-size: 0.875rem;
    line-height: 1.4;
    word-wrap: break-word;
  }

  .error-details {
    margin-top: 0.5rem;
  }

  .error-details details {
    cursor: pointer;
  }

  .error-details summary {
    font-size: 0.75rem;
    color: #9ca3af;
    font-weight: 500;
    padding: 0.25rem 0;
    user-select: none;
  }

  .error-details summary:hover {
    color: #6b7280;
  }

  .error-details-list {
    margin: 0.5rem 0 0 0;
    padding-left: 1rem;
    font-size: 0.75rem;
    color: #6b7280;
  }

  .error-details-list li {
    margin-bottom: 0.25rem;
  }

  .error-details pre {
    font-size: 0.75rem;
    color: #6b7280;
    background-color: #f9fafb;
    padding: 0.5rem;
    border-radius: 0.25rem;
    margin: 0.5rem 0 0 0;
    overflow-x: auto;
    max-width: 100%;
  }

  .error-close {
    background: none;
    border: none;
    font-size: 1.25rem;
    color: #9ca3af;
    cursor: pointer;
    padding: 0.25rem;
    margin: -0.25rem -0.25rem -0.25rem 0;
    line-height: 1;
    border-radius: 0.25rem;
    flex-shrink: 0;
    transition: all 0.2s ease;
  }

  .error-close:hover {
    color: #6b7280;
    background-color: rgba(0, 0, 0, 0.05);
  }

  .error-close:focus {
    outline: 2px solid #3b82f6;
    outline-offset: 1px;
  }

  @keyframes slideIn {
    from {
      transform: translateX(100%);
      opacity: 0;
    }
    to {
      transform: translateX(0);
      opacity: 1;
    }
  }

  /* Responsive design */
  @media (max-width: 640px) {
    .error-container {
      top: 0.5rem;
      right: 0.5rem;
      left: 0.5rem;
      max-width: none;
    }

    .error-message {
      padding: 0.75rem;
      margin-bottom: 0.5rem;
    }

    .error-icon {
      font-size: 1rem;
    }

    .error-title,
    .error-message-text {
      font-size: 0.8125rem;
    }
  }

  /* High contrast mode support */
  @media (prefers-contrast: high) {
    .error-message {
      border-width: 2px;
    }

    .error-close {
      border: 1px solid currentColor;
    }
  }

  /* Reduced motion support */
  @media (prefers-reduced-motion: reduce) {
    .error-message {
      animation: none;
    }
  }
</style>