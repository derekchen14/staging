<script>
	import Application from '../application/+page.svelte';
	import { JWTtoken } from '../store';
	import Login from '../login/+page.svelte';

</script>

{#if $JWTtoken != null }
	<Application />
{:else }
	<Login />
{/if}
