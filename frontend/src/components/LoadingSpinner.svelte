<script lang="ts">
  export let size: 'small' | 'medium' | 'large' = 'medium';
  export let inline: boolean = false;
  export let label: string = 'Loading...';
  export let color: 'primary' | 'secondary' | 'white' = 'primary';
</script>

<div 
  class="spinner-container" 
  class:inline
  role="status" 
  aria-label={label}
  aria-live="polite"
>
  <div 
    class="spinner" 
    class:small={size === 'small'} 
    class:large={size === 'large'}
    class:primary={color === 'primary'}
    class:secondary={color === 'secondary'}
    class:white={color === 'white'}
  >
    <div></div>
    <div></div>
    <div></div>
    <div></div>
  </div>
  <span class="sr-only">{label}</span>
</div>

<style>
  .spinner-container {
    display: flex;
    justify-content: center;
    align-items: center;
    padding: 1rem;
  }

  .spinner-container.inline {
    display: inline-flex;
    padding: 0;
  }

  .spinner {
    display: inline-block;
    position: relative;
    width: 40px;
    height: 40px;
  }

  .spinner.small {
    width: 20px;
    height: 20px;
  }

  .spinner.large {
    width: 60px;
    height: 60px;
  }

  .spinner div {
    box-sizing: border-box;
    display: block;
    position: absolute;
    width: 32px;
    height: 32px;
    margin: 4px;
    border: 3px solid;
    border-radius: 50%;
    animation: spinner 1.2s cubic-bezier(0.5, 0, 0.5, 1) infinite;
  }

  .spinner.primary div {
    border-color: #3b82f6 transparent transparent transparent;
  }

  .spinner.secondary div {
    border-color: #6b7280 transparent transparent transparent;
  }

  .spinner.white div {
    border-color: #ffffff transparent transparent transparent;
  }

  .spinner.small div {
    width: 16px;
    height: 16px;
    margin: 2px;
    border-width: 2px;
  }

  .spinner.large div {
    width: 48px;
    height: 48px;
    margin: 6px;
    border-width: 4px;
  }

  .spinner div:nth-child(1) {
    animation-delay: -0.45s;
  }

  .spinner div:nth-child(2) {
    animation-delay: -0.3s;
  }

  .spinner div:nth-child(3) {
    animation-delay: -0.15s;
  }

  .sr-only {
    position: absolute;
    width: 1px;
    height: 1px;
    padding: 0;
    margin: -1px;
    overflow: hidden;
    clip: rect(0, 0, 0, 0);
    white-space: nowrap;
    border: 0;
  }

  @keyframes spinner {
    0% {
      transform: rotate(0deg);
    }
    100% {
      transform: rotate(360deg);
    }
  }

  /* Respect user's motion preferences */
  @media (prefers-reduced-motion: reduce) {
    .spinner div {
      animation-duration: 2s;
    }
  }

  /* High contrast mode support */
  @media (prefers-contrast: high) {
    .spinner div {
      border-width: 4px;
    }

    .spinner.small div {
      border-width: 3px;
    }
  }
</style>