<script>
	import { page } from '$app/stores';
  	import Logo from './Logo.svelte';
	import { JWTtoken } from './store'
</script>

<header>
	<div class="logo">
		<Logo />
	</div>
	<nav>
		<ul>
			{#if !$JWTtoken}
				<li aria-current={$page.url.pathname === '/application' ? 'page' : undefined}>
					<a href="/login">Try Demo</a>
				</li>
				<li aria-current={$page.url.pathname.startsWith('/login') ? 'page' : undefined}>
					<a href="/login">Log-In</a>
				</li>
				<li aria-current={$page.url.pathname.startsWith('/signup') ? 'page' : undefined}>
					<a href="/signup">Sign-Up</a>
				</li>
			{/if}
			<li aria-current={$page.url.pathname.startsWith('/help') ? 'page' : undefined}>
				<a href="https://www.canva.com/design/DAFn5yv60xM/cF9TPVZuonwnorCHl-5iVQ/watch?utm_content=DAFn5yv60xM&utm_campaign=designshare&utm_medium=link&utm_source=publishsharelink">Help</a>
			</li>
			<li aria-current={$page.url.pathname.startsWith('/feedback') ? 'page' : undefined}>
				<a href="https://x8l3b1ogtwp.typeform.com/to/dXWQchhR">feedback</a>
			</li>
			<li aria-current={$page.url.pathname.startsWith('/blog') ? 'page' : undefined}>
				<a href="https://morethanoneturn.com/">Blog</a>
			</li>
			{#if $JWTtoken}
				<li aria-current={$page.url.pathname === '/application' ? 'page' : undefined}>
					<a href="/application">Dana</a>
				</li>
				<li aria-current={$page.url.pathname.startsWith('/logout') ? 'page' : undefined}>
					<a href="/logout">Log-Out</a>
				</li>
			{/if}
		</ul>
	</nav>
</header>

<style>
	header {
		display: flex;
		justify-content: right;
	}

	.logo {
    margin-right: auto; /* Push the logo to the left */
  	}

	nav {
		display: flex;
		justify-content: right;
		--background: rgba(201, 241, 255, 0);
	}

	ul {
		position: relative;
		padding: 0;
		margin: 0;
		height: 3em;
		display: flex;
		justify-content: center;
		align-items: center;
		list-style: none;
		background: var(--background);
		background-size: contain;
	}

	li {
		position: relative;
		height: 100%;
	}

	li[aria-current='page']::before {
		--size: 6px;
		content: '';
		width: 0;
		height: 0;
		position: absolute;
		top: 0;
		left: calc(50% - var(--size));
		border: var(--size) solid transparent;
		border-top: var(--size) solid var(--color-theme-1);
	}

	nav a {
		display: flex;
		height: 100%;
		align-items: center;
		padding: 0 0.5rem;
		color: var(--color-text);
		font-weight: 700;
		font-size: 0.8rem;
		text-transform: uppercase;
		letter-spacing: 0.1em;
		text-decoration: none;
		transition: color 0.2s linear;
	}

	a:hover {
		color: var(--color-theme-1);
	}
</style>
