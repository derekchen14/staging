<!-- RouteGuard.svelte -->
<script>
    import { onMount } from 'svelte';
    import { JWTtoken } from './store';
    const authenticated = JWTtoken !== null;
  
    onMount(() => {
      // Check if user is authenticated, if not, redirect to login page
      if (!authenticated) {
        // Replace '/login' with the path of your login page
        window.location.href = '/login';
      }
    });
  </script>
  
  {#if authenticated}
    <!-- Render the route content -->
    <slot></slot>
  {:else}
    <!-- Optionally, show a loading state or a message for unauthenticated users -->
    <p>Loading...</p>
  {/if}
  