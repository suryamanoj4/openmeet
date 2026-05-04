<script lang="ts">
	import '../app.css';
	import { onMount } from 'svelte';
	import { goto } from '$app/navigation';
	import { ambientAuth } from '$lib/ambient-auth.svelte';
	import { authStore } from '$lib/stores/auth';
	import { getMe } from '$lib/services/auth';
	import Button from '$lib/components/ui/button.svelte';
	import AuthSlideOver from '$lib/components/auth/auth-slide-over.svelte';
	import { Search, Menu, X } from 'lucide-svelte';
	import type { User } from '$lib/graphql/types';

	let { children }: { children?: import('svelte').Snippet } = $props();

	let mobileMenuOpen = $state(false);

	onMount(async () => {
		const { accessToken } = authStore.loadFromStorage();
		if (accessToken) {
			try {
				const user = await getMe();
				if (user) {
					authStore.setUser(user as User);
				} else {
					authStore.logout();
				}
			} catch {
				authStore.logout();
			}
		} else {
			authStore.setLoading(false);
		}
	});

	function handleLogin() {
		ambientAuth.requireAuth({
			kind: 'login',
			label: 'Sign in',
			execute: () => goto('/dashboard')
		});
	}
</script>

<div class="min-h-screen bg-background">
	<header class="bg-surface-container-lowest/95 backdrop-blur-md fixed top-0 w-full z-50 border-b border-outline-variant/60 shadow-sm">
		<nav class="flex items-center justify-between h-16 px-6 max-w-[1440px] mx-auto">
			<div class="flex items-center gap-8">
				<a href="/" class="flex items-center gap-2">
					<div class="flex h-8 w-8 items-center justify-center rounded-lg bg-primary text-on-primary text-sm font-bold">
						O
					</div>
					<span class="text-headline-md font-bold text-fg">OpenMeet</span>
				</a>
				<div class="hidden md:flex items-center gap-1">
					<a href="/" class="px-3 py-2 text-label-md text-primary font-semibold border-b-2 border-primary transition-colors">
						Explore
					</a>
					<a href="/" class="px-3 py-2 text-label-md text-on-surface-variant hover:text-fg rounded-lg hover:bg-surface-container-low transition-colors">
						Categories
					</a>
					<a href="/" class="px-3 py-2 text-label-md text-on-surface-variant hover:text-fg rounded-lg hover:bg-surface-container-low transition-colors">
						Calendar
					</a>
					<a href="/" class="px-3 py-2 text-label-md text-on-surface-variant hover:text-fg rounded-lg hover:bg-surface-container-low transition-colors">
						Venues
					</a>
				</div>
			</div>

			<div class="flex items-center gap-3">
				<div class="relative hidden lg:block">
					<Search size={16} class="absolute left-3 top-1/2 -translate-y-1/2 text-on-surface-variant" />
					<input
						type="text"
						placeholder="Search events..."
						class="pl-9 pr-4 py-2 bg-surface-container-low border border-outline-variant rounded-full text-body-md focus:ring-2 focus:ring-primary focus:border-transparent outline-none w-56 transition-all placeholder:text-on-surface-variant/60"
					/>
				</div>

				<div class="hidden sm:flex items-center gap-2">
					{#if ambientAuth.isAuthenticated}
						<div class="flex items-center gap-2">
							<a href="/dashboard" class="text-label-md text-on-surface-variant hover:text-fg transition-colors px-3 py-2">
								Dashboard
							</a>
							<span class="text-body-md text-on-surface-variant">{ambientAuth.user?.first_name}</span>
							<Button variant="ghost" size="sm" onclick={() => ambientAuth.logout()}>
								Sign out
							</Button>
						</div>
					{:else}
						<Button variant="ghost" size="sm" onclick={handleLogin}>
							Sign In
						</Button>
						<Button variant="primary" size="sm" onclick={() => goto('/register')}>
							Sign Up
						</Button>
					{/if}
				</div>

				<button
					class="md:hidden flex h-9 w-9 items-center justify-center rounded-lg text-on-surface-variant hover:bg-surface-container-low"
					onclick={() => mobileMenuOpen = !mobileMenuOpen}
				>
					{#if mobileMenuOpen}
						<X size={20} />
					{:else}
						<Menu size={20} />
					{/if}
				</button>
			</div>
		</nav>

		{#if mobileMenuOpen}
			<div class="md:hidden border-t border-outline-variant/60 bg-surface-container-lowest p-4 space-y-2 animate-fade-in">
				<a href="/" class="block px-3 py-2 text-label-md text-primary font-semibold rounded-lg bg-surface-container-low">Explore</a>
				<a href="/" class="block px-3 py-2 text-label-md text-on-surface-variant hover:text-fg rounded-lg hover:bg-surface-container-low">Categories</a>
				<a href="/" class="block px-3 py-2 text-label-md text-on-surface-variant hover:text-fg rounded-lg hover:bg-surface-container-low">Calendar</a>
				<a href="/" class="block px-3 py-2 text-label-md text-on-surface-variant hover:text-fg rounded-lg hover:bg-surface-container-low">Venues</a>
				<hr class="border-outline-variant/60 my-2" />
				{#if ambientAuth.isAuthenticated}
					<a href="/dashboard" class="block px-3 py-2 text-label-md text-on-surface-variant hover:text-fg">Dashboard</a>
					<button class="block w-full text-left px-3 py-2 text-label-md text-on-surface-variant hover:text-fg" onclick={() => ambientAuth.logout()}>Sign out</button>
				{:else}
					<button class="block w-full text-left px-3 py-2 text-label-md text-primary font-semibold" onclick={handleLogin}>Sign In</button>
					<button class="block w-full text-left px-3 py-2 text-label-md text-primary font-semibold" onclick={() => goto('/register')}>Sign Up</button>
				{/if}
			</div>
		{/if}
	</header>

	<main class="pt-16">
		{@render children?.()}
	</main>
</div>

<AuthSlideOver />
