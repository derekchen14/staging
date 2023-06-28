<script>
  import { onMount } from 'svelte';

  let message = '';
  let messages = [];
  let longEnough = false;
  const serverUrl = import.meta.env.VITE_SERVER_URL;

  onMount(async () => {
    const res = await fetch(`${serverUrl}/messages`);
    const data = await res.json();
    messages = data.messages || []; // if messages is undefined, it will be set to an empty array
  });

  $: longEnough = messages.length >= 7;

  async function startOver() {
    const res = await fetch(`${serverUrl}/reset`);
    const { status } = await res.json();

    if (status === 'success') {
      const res = await fetch(`${serverUrl}/messages`);
      const data = await res.json();
      messages = data.messages;
      longEnough = false;
    }
  }

  async function sendMessage() {
    const res = await fetch(`${serverUrl}/messages`, {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({ user: message }),
    });

    message = '';
    const { status } = await res.json();

    if (status === 'success') {
      const res = await fetch(`${serverUrl}/messages`);
      const data = await res.json();
      messages = data.messages;
    }
  }
</script>

<main>
  <h1>Soleda Chatbot</h1>
  <input bind:value={message} placeholder="Type a message..." />
  <button on:click={sendMessage}>Send</button>

  <ul>
    {#each messages as msg}
      <li><strong>User:</strong> {msg.user}</li>
      <li><strong>Bot:</strong> {msg.bot}</li>
    {/each}
  </ul>

  {#if longEnough}
    <button on:click={startOver}>Start Over</button>
  {/if}
</main>


<style>
  ul { 
    list-style-type: none;
    text-align: left;
  }
</style>