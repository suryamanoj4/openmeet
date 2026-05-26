<script lang="ts">
	import { goto } from '$app/navigation';
	import AuthSlideOver from '$lib/components/auth/auth-slide-over.svelte';
	import { ambientAuth } from '$lib/ambient-auth.svelte';
	import Button from '$lib/components/ui/button.svelte';

	let { children }: { children?: import('svelte').Snippet } = $props();
</script>

<div class="min-h-screen bg-background">
	<header class="sticky top-0 z-40 border-b border-outline-variant/60 bg-surface-container-lowest/80 backdrop-blur-lg">
		<div class="mx-auto flex h-14 max-w-7xl items-center justify-between px-6">
			<a href="/" class="flex items-center gap-2">
				<div class="flex h-7 w-7 items-center justify-center rounded-md bg-primary text-on-primary text-xs font-bold">O</div>
				<span class="text-headline-md font-bold text-fg">OpenMeet</span>
			</a>
			<nav class="flex items-center gap-3">
				{#if ambientAuth.isAuthenticated}
					<Button variant="ghost" size="sm" onclick={() => goto('/dashboard')}>Dashboard</Button>
				{:else}
					<Button variant="ghost" size="sm" onclick={() => ambientAuth.requireAuth({ kind: 'login', label: 'Sign in', execute: () => goto('/dashboard') })}>Sign In</Button>
				{/if}
			</nav>
		</div>
	</header>
	<main>{@render children?.()}</main>
</div>
<AuthSlideOver />
