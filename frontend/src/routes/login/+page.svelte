<script>
	import { JWTtoken } from '../store';

	let username = '';
	let password = '';
	let error = ''

	const getUserDetails = async (username, password) => {
	// Make a POST request to the backend API for user login
	const response = await fetch('http://localhost:8000/user/login', {
		method: 'POST',
		headers: {
		'Content-Type': 'application/json',
		},
		body: JSON.stringify({
			email: username,  // In the backend, the email field is used for login, so we'll use it here as the username
			password: password,
		}),
	});

	const data = await response.json(); // Assuming the response is JSON data, parse it
	return data; // Return the response data to handle it in the calling function
	}

	async function login() {
		console.log("In login")
		const response = await getUserDetails( username, password )

		if (response) {
			$JWTtoken = response;
		} else {
			error = 'Incorrect username and password.';
			console.log('Incorrect username and password.');
  		}
	}

</script>

<form on:submit|preventDefault={login} class="flex mx-auto col-6">

	<div class="mb-3">
		<label for="username" class="form-label">Username</label>
		<input type="email" class="form-control" id="username" bind:value={username} />
	</div>

	<div class="mb-3">
		<label for="password" class="form-label">Password</label>
		<input type="password" class="form-control" id="password" bind:value={password} />
	</div>

	<button type="submit" class="btn btn-primary">Submit</button>
	<div id="error_message" class="text-danger">
		<small>{error}</small>
	</div>

</form>

