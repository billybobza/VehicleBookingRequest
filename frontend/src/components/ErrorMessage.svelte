<script lang="ts">
  export let message: string;
  export let type: 'error' | 'warning' | 'info' = 'error';
  export let dismissible: boolean = false;
  export let onDismiss: (() => void) | undefined = undefined;

  function handleDismiss() {
    if (onDismiss) {
      onDismiss();
    }
  }
</script>

<div 
  class="message" 
  class:error={type === 'error'}
  class:warning={type === 'warning'}
  class:info={type === 'info'}
  role="alert"
  aria-live="polite"
>
  <div class="message-icon">
    {#if type === 'error'}
      <span aria-hidden="true">❌</span>
    {:else if type === 'warning'}
      <span aria-hidden="true">⚠️</span>
    {:else}
      <span aria-hidden="true">ℹ️</span>
    {/if}
  </div>
  <div class="message-content">
    {message}
  </div>
  {#if dismissible}
    <button 
      class="message-dismiss"
      on:click={handleDismiss}
      aria-label="Dismiss message"
      title="Dismiss message"
    >
      <span aria-hidden="true">×</span>
    </button>
  {/if}
</div>

<style>
  .message {
    border-radius: 0.5rem;
    padding: 0.75rem;
    margin: 0.5rem 0;
    font-size: 0.875rem;
    display: flex;
    align-items: flex-start;
    gap: 0.5rem;
    border-left: 4px solid;
  }

  .message.error {
    background-color: #fef2f2;
    border-color: #fecaca;
    border-left-color: #ef4444;
    color: #991b1b;
  }

  .message.warning {
    background-color: #fffbeb;
    border-color: #fed7aa;
    border-left-color: #f59e0b;
    color: #92400e;
  }

  .message.info {
    background-color: #eff6ff;
    border-color: #bfdbfe;
    border-left-color: #3b82f6;
    color: #1e40af;
  }

  .message-icon {
    flex-shrink: 0;
    font-size: 1rem;
    margin-top: 0.125rem;
  }

  .message-content {
    flex: 1;
    line-height: 1.4;
  }

  .message-dismiss {
    background: none;
    border: none;
    font-size: 1.25rem;
    cursor: pointer;
    padding: 0.125rem;
    margin: -0.125rem -0.125rem -0.125rem 0;
    line-height: 1;
    border-radius: 0.25rem;
    flex-shrink: 0;
    color: inherit;
    opacity: 0.7;
    transition: all 0.2s ease;
  }

  .message-dismiss:hover {
    opacity: 1;
    background-color: rgba(0, 0, 0, 0.1);
  }

  .message-dismiss:focus {
    outline: 2px solid currentColor;
    outline-offset: 1px;
    opacity: 1;
  }

  /* High contrast mode support */
  @media (prefers-contrast: high) {
    .message {
      border-width: 2px;
    }

    .message-dismiss {
      border: 1px solid currentColor;
    }
  }
</style>