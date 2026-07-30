<script lang="ts">
	import '../app.css';
	import { onMount } from 'svelte';
	import { goto } from '$app/navigation';
	import { page } from '$app/state';
	import { ambientAuth } from '$lib/ambient-auth.svelte';
	import { authStore, isAuthenticated, currentUser } from '$lib/stores/auth';
	import { getMe } from '$lib/services/auth';
	import Button from '$lib/components/ui/button.svelte';
	import AuthSlideOver from '$lib/components/auth/auth-slide-over.svelte';
	import { Search, Menu, Plus, X } from 'lucide-svelte';
	import type { User } from '$lib/graphql/types';

	let { children }: { children?: import('svelte').Snippet } = $props();

	let mobileMenuOpen = $state(false);
	let headerSearch = $state('');
	let activeView = $derived(
		page.url.pathname === '/' ? (page.url.searchParams.get('view') ?? 'explore') : ''
	);

	$effect(() => {
		if (page.url.pathname === '/') {
			headerSearch = page.url.searchParams.get('q') ?? '';
		}
	});

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

	function discoveryClass(view: string): string {
		return activeView === view
			? 'px-3 py-2 text-label-md text-primary font-semibold border-b-2 border-primary transition-colors'
			: 'px-3 py-2 text-label-md text-on-surface-variant hover:text-fg rounded-lg hover:bg-surface-container-low transition-colors';
	}

	function handleHeaderSearch(event: SubmitEvent) {
		event.preventDefault();
		const params =
			page.url.pathname === '/'
				? new URLSearchParams(page.url.searchParams)
				: new URLSearchParams();
		params.set('view', 'explore');
		if (headerSearch.trim()) params.set('q', headerSearch.trim());
		else params.delete('q');
		goto(`/?${params.toString()}#discover`);
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
					<a href="/?view=explore#discover" class={discoveryClass('explore')}>
						Explore
					</a>
					<a href="/?view=categories#discover" class={discoveryClass('categories')}>
						Categories
					</a>
					<a href="/?view=calendar&sort=date#discover" class={discoveryClass('calendar')}>
						Calendar
					</a>
					<a href="/?view=venues#discover" class={discoveryClass('venues')}>
						Venues
					</a>
				</div>
			</div>

			<div class="flex items-center gap-3">
				<form class="relative hidden lg:block" onsubmit={handleHeaderSearch}>
					<Search size={16} class="absolute left-3 top-1/2 -translate-y-1/2 text-on-surface-variant pointer-events-none" />
					<input
						type="text"
						placeholder="Search events..."
						aria-label="Search events"
						bind:value={headerSearch}
						class="pl-9 pr-4 py-2 bg-surface-container-low border border-outline-variant rounded-full text-body-md focus:ring-2 focus:ring-primary focus:border-transparent outline-none w-56 transition-all placeholder:text-on-surface-variant/60"
					/>
				</form>

				<div class="hidden sm:flex items-center gap-2">
					{#if $isAuthenticated}
						<Button variant="primary" size="sm" onclick={() => goto('/events/new')}>
							<Plus size={16} class="mr-1" />
							Create Event
						</Button>
						<a
							href="/dashboard"
							class="flex h-9 w-9 items-center justify-center rounded-full bg-primary text-on-primary text-label-sm font-bold hover:bg-primary-container hover:text-on-primary-container transition-colors"
							title="Dashboard"
						>
							{($currentUser?.first_name?.[0] ?? 'U').toUpperCase()}
						</a>
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
				<form class="relative mb-3" onsubmit={handleHeaderSearch}>
					<Search size={16} class="absolute left-3 top-1/2 -translate-y-1/2 text-on-surface-variant pointer-events-none" />
					<input type="search" placeholder="Search events..." aria-label="Search events" bind:value={headerSearch} class="w-full h-10 pl-9 pr-4 rounded-lg border border-outline-variant bg-surface-container-low text-body-md outline-none focus:ring-2 focus:ring-primary" />
				</form>
				<a href="/?view=explore#discover" class="block px-3 py-2 text-label-md text-on-surface-variant hover:text-fg rounded-lg hover:bg-surface-container-low">Explore</a>
				<a href="/?view=categories#discover" class="block px-3 py-2 text-label-md text-on-surface-variant hover:text-fg rounded-lg hover:bg-surface-container-low">Categories</a>
				<a href="/?view=calendar&sort=date#discover" class="block px-3 py-2 text-label-md text-on-surface-variant hover:text-fg rounded-lg hover:bg-surface-container-low">Calendar</a>
				<a href="/?view=venues#discover" class="block px-3 py-2 text-label-md text-on-surface-variant hover:text-fg rounded-lg hover:bg-surface-container-low">Venues</a>
				<hr class="border-outline-variant/60 my-2" />
				{#if $isAuthenticated}
					<a href="/events/new" class="flex items-center gap-2 px-3 py-2 text-label-md font-semibold text-primary rounded-lg bg-primary-fixed">
						<Plus size={16} /> Create Event
					</a>
					<a href="/dashboard" class="block px-3 py-2 text-label-md text-on-surface-variant hover:text-fg rounded-lg hover:bg-surface-container-low">Dashboard</a>
					<button class="block w-full text-left px-3 py-2 text-label-md text-on-surface-variant hover:text-fg rounded-lg hover:bg-surface-container-low" onclick={() => ambientAuth.logout()}>Sign out</button>
				{:else}
					<button class="block w-full text-left px-3 py-2 text-label-md text-primary font-semibold rounded-lg hover:bg-surface-container-low" onclick={handleLogin}>Sign In</button>
					<button class="block w-full text-left px-3 py-2 text-label-md text-primary font-semibold rounded-lg hover:bg-surface-container-low" onclick={() => goto('/register')}>Sign Up</button>
				{/if}
			</div>
		{/if}
	</header>

	<main class="pt-16">
		{@render children?.()}
	</main>
</div>

<AuthSlideOver />
