<!-- Signup.svelte -->
<script>
  import { onMount } from 'svelte';
  import { getUserDetails } from '/Users/bestc/Soleda/staging/new_frontend/src/hooks/auth.js'; // Import the getUserDetails function from auth.js
  import {users} from '/Users/bestc/Soleda/staging/new_frontend/src/hooks/auth.js';
  let username = '';
  let password = '';
  let feedback = '';

  const signup = async () => {
    // Call the getUserDetails function to check if the user already exists
    const result = await getUserDetails(username, password);

    if (result === 1) {
      feedback = 'User already exists! Please choose a different username.';
    } else {
      // Handle user creation logic here, e.g., adding the user to the users array
      // For simplicity, we will assume the user is added directly to the array
      users.push({ username, password });
      feedback = 'User created successfully!';
    }
  };
</script>

<main>
  <h1>Signup Page</h1>
  <input bind:value={username} type="text" placeholder="Username" />
  <input bind:value={password} type="password" placeholder="Password" />
  <button on:click={signup}>Signup</button>
  {#if feedback}
    <p>{feedback}</p>
  {/if}
</main>

<style>
  /* Add your CSS styles here */
</style>
