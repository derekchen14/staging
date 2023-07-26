<script>
    import { onMount } from 'svelte';

    let first = '';
    let last = '';
    let email = '';
    let password = '';
    let feedback = '';

    const handleSignup = async () => {
    //Takes in the users' inputs to form fields.
      if (!first || !last || !email || !password) {
        feedback = 'Please fill in all the fields.';
        return;
      }
      const user = {
        first: first, // The user's first name, taken from the firstField variable
        last: last, // The user's last name, taken from the lastField variable
        email: email, // The user's email (username)
        password: password, // The user's password   
      };
  
      const response = await signup(user);
      if (response.ok) {
        console.log("response is: ", response)
        feedback = 'User created successfully!';
      } else {
        feedback = 'User already exists. Please try again.';
      }
    }

    const signup = async (user) => { 
    // Make a POST request to the backend API for user signup
    const response = await fetch('http://localhost:8000/user/signup', {
        method: 'POST',
        headers: {
        'Content-Type': 'application/json',
        },
        body: JSON.stringify(user),
    });
    console.log("This is the unparsed data: ", response)
    const data = await response.json(); // Assuming the response is JSON data, parse it
    console.log("This is the parsed data: ", data)
    
    return response; // Return the response data to handle it in the calling function
    }
  </script>
  
  <main>
  
    <form on:submit|preventDefault={handleSignup} class="flex mx-auto col-6">
  
      <div class="mb-3">
        <label for="first" class="form-label">First Name</label>
        <input type="text" class="form-control" id="first" bind:value={first} />
      </div>
  
      <div class="mb-3">
        <label for="last" class="form-label">Last Name</label>
        <input type="text" class="form-control" id="last" bind:value={last} />
      </div>
  
      <div class="mb-3">
        <label for="email" class="form-label">Email</label>
        <input type="text" class="form-control" id="email" bind:value={email} />
      </div>
  
      <div class="mb-3">
        <label for="password" class="form-label">Password</label>
        <input type="password" class="form-control" id="password" bind:value={password} />
      </div>
      
      <div class="submit-container">
      <button type="submit" class="btn btn-primary">Signup</button>
      </div>

      <!-- Use the error variable to display any signup feedback -->
      <div class="text-danger">
        {#if feedback}
          <p>{feedback}</p>
        {/if}
      </div>
  
    </form>
  </main>
  
  <style>
	/* Center the form horizontally */
	form {
	  display: flex;
	  flex-direction: column;
	  align-items: center;
	  justify-content: center;
	  height: 100vh;
	}
  
	.form-label {
	  display: block;
	  font-size: 1rem;
	  font-weight: bold;
	  margin-bottom: 0.5rem;
	}
  
	.form-control {
	  width: 100%;
	  padding: 0.5rem;
	  font-size: 1rem;
	  border: 1px solid #ccc;
	  border-radius: 0.25rem;
	}
  
	.btn-primary {
	  padding: 0.5rem 1rem;
	  font-size: 1rem;
	  border: none;
	  border-radius: 0.25rem;
	  background-color: #007bff;
	  color: #fff;
	  cursor: pointer;
	  margin-top: 1rem;

	}
  
	.btn-primary:hover {
	  background-color: #0056b3;
	}
  
	.text-danger {
	  color: #dc3545;
	  font-size: 0.875rem;
	  margin-top: 0.25rem;
	}
  </style>