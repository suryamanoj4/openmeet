<script lang="ts">
	import { goto } from '$app/navigation';
	import { ambientAuth } from '$lib/ambient-auth.svelte';
	import Button from '$lib/components/ui/button.svelte';

	function handleCreateOrg() {
		if (ambientAuth.isAuthenticated) {
			goto('/organization/new');
		} else {
			ambientAuth.requireAuth({
				kind: 'create-org',
				label: 'Create an organization',
				execute: () => goto('/organization/new')
			});
		}
	}

	function handleCreateEvent() {
		if (ambientAuth.isAuthenticated) {
			goto('/events/new');
		} else {
			ambientAuth.requireAuth({
				kind: 'create-event',
				label: 'Create an event',
				execute: () => goto('/events/new')
			});
		}
	}
</script>

<div class="mx-auto max-w-7xl px-6 py-8">
	{#if ambientAuth.isAuthenticated}
		<div class="animate-fade-in">
			<div class="mb-8">
				<h1 class="text-headline-xl font-bold text-fg">Dashboard</h1>
				<p class="mt-1 text-body-lg text-on-surface-variant">
					Welcome back, {ambientAuth.user?.first_name ?? 'User'}
				</p>
			</div>

			<div class="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
				<div class="rounded-xl border border-outline-variant bg-card p-6 shadow-sm">
					<div class="flex items-center gap-3">
						<div class="flex h-10 w-10 items-center justify-center rounded-lg bg-primary-fixed text-on-primary-fixed">
							<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M22 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/></svg>
						</div>
						<div>
							<p class="text-label-sm text-on-surface-variant">Organizations</p>
							<p class="text-headline-lg font-bold text-fg">0</p>
						</div>
					</div>
				</div>
				<div class="rounded-xl border border-outline-variant bg-card p-6 shadow-sm">
					<div class="flex items-center gap-3">
						<div class="flex h-10 w-10 items-center justify-center rounded-lg bg-secondary-fixed text-on-secondary-fixed">
							<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="4" width="18" height="18" rx="2" ry="2"/><line x1="16" y1="2" x2="16" y2="6"/><line x1="8" y1="2" x2="8" y2="6"/><line x1="3" y1="10" x2="21" y2="10"/></svg>
						</div>
						<div>
							<p class="text-label-sm text-on-surface-variant">Events</p>
							<p class="text-headline-lg font-bold text-fg">0</p>
						</div>
					</div>
				</div>
				<div class="rounded-xl border border-outline-variant bg-card p-6 shadow-sm">
					<div class="flex items-center gap-3">
						<div class="flex h-10 w-10 items-center justify-center rounded-lg bg-tertiary-fixed text-on-tertiary-fixed">
							<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M6 2 3 6v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2V6l-3-4Z"/><path d="M3 6h18"/><path d="M16 10a4 4 0 0 1-8 0"/></svg>
						</div>
						<div>
							<p class="text-label-sm text-on-surface-variant">Tickets Sold</p>
							<p class="text-headline-lg font-bold text-fg">0</p>
						</div>
					</div>
				</div>
				<div class="rounded-xl border border-outline-variant bg-card p-6 shadow-sm">
					<div class="flex items-center gap-3">
						<div class="flex h-10 w-10 items-center justify-center rounded-lg bg-surface-container-high text-on-surface">
							<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="12" y1="2" x2="12" y2="6"/><line x1="12" y1="18" x2="12" y2="22"/><line x1="4.93" y1="4.93" x2="7.76" y2="7.76"/><line x1="16.24" y1="16.24" x2="19.07" y2="19.07"/><line x1="2" y1="12" x2="6" y2="12"/><line x1="18" y1="12" x2="22" y2="12"/><line x1="4.93" y1="19.07" x2="7.76" y2="16.24"/><line x1="16.24" y1="7.76" x2="19.07" y2="4.93"/></svg>
						</div>
						<div>
							<p class="text-label-sm text-on-surface-variant">Revenue</p>
							<p class="text-headline-lg font-bold text-fg">$0</p>
						</div>
					</div>
				</div>
			</div>

			<div class="mt-8 rounded-xl border border-outline-variant bg-card p-6 shadow-sm">
				<h2 class="text-headline-md font-semibold text-fg">Getting started</h2>
				<p class="text-body-md text-on-surface-variant mt-1">Follow these steps to launch your first event</p>
				<ol class="mt-6 space-y-4">
					<li class="flex items-start gap-4">
						<span class="flex h-8 w-8 shrink-0 items-center justify-center rounded-lg bg-primary text-on-primary text-label-sm font-bold">1</span>
						<div>
							<p class="text-label-md text-fg">Create your first organization</p>
							<p class="text-body-md text-on-surface-variant">Set up your team and event brand</p>
						</div>
					</li>
					<li class="flex items-start gap-4">
						<span class="flex h-8 w-8 shrink-0 items-center justify-center rounded-lg bg-primary text-on-primary text-label-sm font-bold">2</span>
						<div>
							<p class="text-label-md text-fg">Add team members</p>
							<p class="text-body-md text-on-surface-variant">Collaborate with your team</p>
						</div>
					</li>
					<li class="flex items-start gap-4">
						<span class="flex h-8 w-8 shrink-0 items-center justify-center rounded-lg bg-primary text-on-primary text-label-sm font-bold">3</span>
						<div>
							<p class="text-label-md text-fg">Create an event</p>
							<p class="text-body-md text-on-surface-variant">Build your event page with our drag-and-drop builder</p>
						</div>
					</li>
					<li class="flex items-start gap-4">
						<span class="flex h-8 w-8 shrink-0 items-center justify-center rounded-lg bg-primary text-on-primary text-label-sm font-bold">4</span>
						<div>
							<p class="text-label-md text-fg">Set up ticket types</p>
							<p class="text-body-md text-on-surface-variant">Configure pricing, tiers, and availability</p>
						</div>
					</li>
					<li class="flex items-start gap-4">
						<span class="flex h-8 w-8 shrink-0 items-center justify-center rounded-lg bg-primary text-on-primary text-label-sm font-bold">5</span>
						<div>
							<p class="text-label-md text-fg">Share and sell tickets</p>
							<p class="text-body-md text-on-surface-variant">Publish your event and start selling</p>
						</div>
					</li>
				</ol>
			</div>
		</div>
	{:else}
		<div class="animate-fade-in">
			<div class="mx-auto max-w-lg rounded-2xl border border-outline-variant bg-surface-container-lowest p-12 text-center shadow-sm">
				<div class="mx-auto flex h-16 w-16 items-center justify-center rounded-2xl bg-primary-fixed">
					<svg xmlns="http://www.w3.org/2000/svg" width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" class="text-primary"><rect x="3" y="3" width="18" height="18" rx="2" ry="2"/><line x1="3" y1="9" x2="21" y2="9"/><line x1="9" y1="21" x2="9" y2="9"/></svg>
				</div>
				<h1 class="mt-5 text-headline-xl font-bold text-fg">Dashboard</h1>
				<p class="mt-2 text-body-lg text-on-surface-variant">
					Sign in to see your dashboard, manage events, and track sales.
				</p>
				<div class="mt-8 flex items-center justify-center gap-3">
					<Button variant="primary" size="lg" onclick={() => ambientAuth.requireAuth({
						kind: 'view-dashboard',
						label: 'View dashboard',
						execute: () => {}
					})}>
						Sign in
					</Button>
					<Button variant="outline" size="lg" onclick={() => goto('/register')}>
						Create an account
					</Button>
				</div>
			</div>
		</div>
	{/if}
</div>
