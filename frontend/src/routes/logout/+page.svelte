<script>
  import { onMount } from "svelte";
  import { JWTtoken } from '../store';

  async function handleLogout() {
    $JWTtoken = '';
    try {
        const response = await fetch("http://localhost:8000/user/logout", {
            method: "POST",
            credentials: "include"
      });
      const data = await response.json();
      console.log(data.message); // Optional: You can use this message to show a success message to the user.

      // Redirect to the homepage after successful logout
      window.location.href = "/"; // Replace "/" with the URL of your homepage
    } catch (error) {
      console.error("Logout failed:", error);
    }
  }

  onMount(() => {
    handleLogout(); // Automatically call handleLogout when the component is mounted
  });
</script>


<p> User logged out from the system.</p>