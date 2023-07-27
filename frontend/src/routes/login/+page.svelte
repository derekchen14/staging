<script>
	import { JWTtoken } from '../store';

	let email = '';
	let password = '';
	let error = ''

	function parseCookies() {
	const cookies = document.cookie.split(';').reduce((cookiesObject, cookie) => {
		const [name, value] = cookie.split('=');
		cookiesObject[name.trim()] = decodeURIComponent(value.trim());
		return cookiesObject;
	}, {});

	return cookies;
	}

	const getUserDetails = async (email, password) => {
	// Make a POST request to the backend API for user login
		const response = await fetch('http://localhost:8000/user/login', {
			method: 'POST',
			headers: {
			'Content-Type': 'application/json',
			},
			body: JSON.stringify({
				email: email, 
				password: password,
			}),
			credentials: 'include',
		});
		const cookies = parseCookies();
		const access_token = cookies.access_token; 
		if (access_token != null) {
			$JWTtoken = access_token;
		}
		return response;
	}

	async function login() {
		if (email.trim() === '' || password.trim() === ''){
			error = 'Please fill in email and password.';
			return ;
		}

		try {
			const response = await getUserDetails(email, password);
			
			if (response.ok) {
				error = 'You have successfully logged in.';
				window.location.href = '/application';
			} else {
			error = 'Incorrect email and password.';
			redirect: '/application'
			}
		} catch (error) {
			console.error(error);
			error = 'An error occurred during login.';
		}
	}
	
</script>

<form on:submit|preventDefault={login} class="flex mx-auto col-6">

	<div class="mb-3">
		<label for="email" class="form-label">Email</label>
		<input type="email" class="form-control" id="email" bind:value={email} />
	</div>

	<div class="mb-3">
		<label for="password" class="form-label">Password</label>
		<input type="password" class="form-control" id="password" bind:value={password} />
	</div>

	<div class="submit-container">
	<button type="submit" class="btn btn-primary">Submit</button>
	</div>

	<div id="error_message" class="text-danger">
		<small>{error}</small>
	</div>

</form>

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