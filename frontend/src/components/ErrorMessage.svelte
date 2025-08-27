<script lang="ts">
  export let message: string;
</script>

<div class="error-message" role="alert">
  {message}
</div>

<style>
  .error-message {
    background-color: #fee;
    border: 1px solid #fcc;
    border-radius: 4px;
    padding: 0.75rem;
    margin: 0.5rem 0;
    color: #c33;
    font-size: 0.875rem;
  }
</style>