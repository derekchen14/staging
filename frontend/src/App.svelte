<script>
  import { onMount } from 'svelte';

  let message = '';
  let messages = [];
  const serverUrl = import.meta.env.VITE_SERVER_URL;

  onMount(async () => {
    const res = await fetch(`http://${serverUrl}/messages`);
    const data = await res.json();
    messages = data.messages || []; // if messages is undefined, it will be set to an empty array
  });

  async function sendMessage() {
    const res = await fetch(`http://${serverUrl}/messages`, {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({ user: message }),
    });

    message = '';
    const { status } = await res.json();

    if (status === 'success') {
      const res = await fetch(`http://${serverUrl}/messages`);
      const data = await res.json();
      messages = data.messages;
    }
  }
</script>

<main>
  <h1>My Chatbot</h1>
  <input bind:value={message} placeholder="Type a message..." />
  <button on:click={sendMessage}>Send</button>

  <ul>
    {#each messages as msg}
      <li><strong>User:</strong> {msg.user}</li>
      <li><strong>Bot:</strong> {msg.bot}</li>
    {/each}
  </ul>
</main>


<style>
  ul { 
    list-style-type: none;
    text-align: left;
  }
</style>