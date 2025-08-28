<script lang="ts">
  import { successNotifications, removeSuccess } from '../stores/ui.js';
  
  function handleClose(notificationId: string) {
    removeSuccess(notificationId);
  }

  // Auto-focus on first success for screen readers
  let successContainer: HTMLDivElement;
  
  $: if ($successNotifications.length > 0 && successContainer) {
    const firstSuccess = successContainer.querySelector('.success-message');
    if (firstSuccess) {
      (firstSuccess as HTMLElement).focus();
    }
  }
</script>

{#if $successNotifications.length > 0}
  <div class="success-container" bind:this={successContainer} aria-live="polite" aria-label="Success notifications">
    {#each $successNotifications as notification (notification.id)}
      <div 
        class="success-message" 
        role="status" 
        tabindex="-1"
        aria-label="Success notification"
      >
        <div class="success-icon">
          ✅
        </div>
        <div class="success-content">
          <div class="success-title">Success</div>
          <div class="success-message-text">{notification.message}</div>
        </div>
        <button 
          class="success-close" 
          on:click={() => handleClose(notification.id)}
          aria-label="Close success message"
          title="Close success message"
        >
          <span aria-hidden="true">×</span>
        </button>
      </div>
    {/each}
  </div>
{/if}

<style>
  .success-container {
    position: fixed;
    top: 1rem;
    right: 1rem;
    z-index: 1000;
    max-width: 420px;
    pointer-events: none;
  }

  .success-message {
    background-color: #f0fdf4;
    border: 1px solid #bbf7d0;
    border-left: 4px solid #22c55e;
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

  .success-message:focus {
    outline: 2px solid #3b82f6;
    outline-offset: 2px;
  }

  .success-icon {
    font-size: 1.25rem;
    flex-shrink: 0;
    margin-top: 0.125rem;
  }

  .success-content {
    flex: 1;
    min-width: 0;
  }

  .success-title {
    font-weight: 600;
    font-size: 0.875rem;
    color: #166534;
    margin-bottom: 0.25rem;
  }

  .success-message-text {
    color: #15803d;
    font-size: 0.875rem;
    line-height: 1.4;
    word-wrap: break-word;
  }

  .success-close {
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

  .success-close:hover {
    color: #6b7280;
    background-color: rgba(0, 0, 0, 0.05);
  }

  .success-close:focus {
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
    .success-container {
      top: 0.5rem;
      right: 0.5rem;
      left: 0.5rem;
      max-width: none;
    }

    .success-message {
      padding: 0.75rem;
      margin-bottom: 0.5rem;
    }

    .success-icon {
      font-size: 1rem;
    }

    .success-title,
    .success-message-text {
      font-size: 0.8125rem;
    }
  }

  /* High contrast mode support */
  @media (prefers-contrast: high) {
    .success-message {
      border-width: 2px;
    }

    .success-close {
      border: 1px solid currentColor;
    }
  }

  /* Reduced motion support */
  @media (prefers-reduced-motion: reduce) {
    .success-message {
      animation: none;
    }
  }
</style>