<script lang="ts">
  export let size: 'small' | 'medium' | 'large' = 'medium';
  export let inline: boolean = false;
</script>

<div class="spinner-container" class:inline>
  <div class="spinner" class:small={size === 'small'} class:large={size === 'large'}>
    <div></div>
    <div></div>
    <div></div>
    <div></div>
  </div>
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
    border: 3px solid #007bff;
    border-radius: 50%;
    animation: spinner 1.2s cubic-bezier(0.5, 0, 0.5, 1) infinite;
    border-color: #007bff transparent transparent transparent;
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

  @keyframes spinner {
    0% {
      transform: rotate(0deg);
    }
    100% {
      transform: rotate(360deg);
    }
  }
</style>