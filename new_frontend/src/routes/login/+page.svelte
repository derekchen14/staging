<script>
	import Application from '../../components/Application.svelte';
	import { store } from '/Users/bestc/Soleda/staging/new_frontend/src/hooks/auth.js';
	import LoginComponent from '/Users/bestc/Soleda/staging/new_frontend/src/components/LoginComponent.svelte';

</script>

{#if $store != null }
	<Application />
{:else }
	<LoginComponent />
{/if}
