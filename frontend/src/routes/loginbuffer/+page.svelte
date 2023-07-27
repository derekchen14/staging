<script>
	import Application from '../application/+page.svelte';
	import { JWTtoken } from '../store';
	import Login from '../login/+page.svelte';
	console.log("JWTtoken is: ", $JWTtoken);
	let authorized = $JWTtoken !== null && $JWTtoken !== '';


</script>

{#if authorized }
	<Application />
{:else }
	<Login />
{/if}
