<script lang="ts">
	import { onMount } from 'svelte';
	import { goto } from '$app/navigation';
	import { listOrganizations } from '$lib/services/organizations';
	import Button from '$lib/components/ui/button.svelte';
	import Card from '$lib/components/ui/card.svelte';
	import { Building2, Plus, ArrowRight } from 'lucide-svelte';
	import type { Organization } from '$lib/graphql/types';

	let orgs = $state<Organization[]>([]);
	let loading = $state(true);

	onMount(async () => {
		orgs = await listOrganizations();
		loading = false;
	});
</script>

<div class="mx-auto max-w-7xl px-6 py-8">
	<div class="flex items-center justify-between mb-8">
		<div>
			<h1 class="text-headline-xl font-bold text-fg">Organizations</h1>
			<p class="text-body-md text-on-surface-variant mt-1">Manage your organizations and teams</p>
		</div>
		<Button variant="primary" size="lg" onclick={() => goto('/organizations/new')}>
			<Plus size={18} class="mr-1.5" />
			New Organization
		</Button>
	</div>

	{#if loading}
		<div class="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
			{#each [1,2,3] as _}
				<div class="h-40 rounded-xl bg-surface-container animate-pulse" />
			{/each}
		</div>
	{:else if orgs.length === 0}
		<div class="rounded-xl border border-outline-variant bg-surface-container-lowest p-16 text-center">
			<div class="mx-auto flex h-16 w-16 items-center justify-center rounded-2xl bg-surface-container-low">
				<Building2 size={32} class="text-on-surface-variant" />
			</div>
			<h3 class="mt-4 text-headline-md font-semibold text-fg">No organizations yet</h3>
			<p class="mt-2 text-body-md text-on-surface-variant">Create your first organization to start managing events.</p>
			<Button variant="primary" size="lg" class="mt-6" onclick={() => goto('/organizations/new')}>
				Create Organization
			</Button>
		</div>
	{:else}
		<div class="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
			{#each orgs as org}
				<Card class="p-6 cursor-pointer hover:shadow-md transition-shadow" onclick={() => goto(`/organizations/${org.id}`)}>
					<div class="flex items-start gap-4">
						<div class="flex h-12 w-12 shrink-0 items-center justify-center rounded-xl bg-primary-fixed text-on-primary-fixed">
							<Building2 size={24} />
						</div>
						<div class="flex-1 min-w-0">
							<h3 class="text-headline-md font-semibold text-fg truncate">{org.name}</h3>
							<p class="text-body-md text-on-surface-variant mt-0.5 truncate">{org.description || 'No description'}</p>
							<div class="flex items-center gap-3 mt-3">
								<span class="text-label-sm text-on-surface-variant">@{org.slug}</span>
								{#if org.is_verified}
									<span class="rounded-full bg-primary-fixed-dim px-2 py-0.5 text-label-sm text-on-primary-fixed-variant">Verified</span>
								{/if}
							</div>
						</div>
						<ArrowRight size={18} class="text-on-surface-variant shrink-0 mt-2" />
					</div>
				</Card>
			{/each}
		</div>
	{/if}
</div>
