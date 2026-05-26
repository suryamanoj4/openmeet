<script lang="ts">
	import { onMount } from 'svelte';
	import { goto } from '$app/navigation';
	import { page } from '$app/stores';
	import { getOrganization, getMembers } from '$lib/services/organizations';
	import Button from '$lib/components/ui/button.svelte';
	import Card from '$lib/components/ui/card.svelte';
	import { ArrowLeft, Building2, Users, ExternalLink, Settings } from 'lucide-svelte';
	import type { Organization } from '$lib/graphql/types';

	let org = $state<Organization | null>(null);
	let members = $state<{ id: string; user_id: string; role: string; is_active: boolean }[]>([]);
	let loading = $state(true);

	onMount(async () => {
		const id = $page.params.id as string;
		org = await getOrganization(id);
		members = await getMembers(id);
		loading = false;
	});
</script>

<div class="mx-auto max-w-4xl px-6 py-8">
	<button onclick={() => goto('/organizations')} class="flex items-center gap-2 text-body-md text-on-surface-variant hover:text-fg mb-6 transition-colors">
		<ArrowLeft size={18} />
		Organizations
	</button>

	{#if loading}
		<div class="h-64 rounded-xl bg-surface-container animate-pulse"></div>
	{:else if !org}
		<div class="text-center py-16"><p class="text-body-lg text-on-surface-variant">Organization not found</p></div>
	{:else}
		{@const oid = org.id}

		<div class="flex items-start justify-between mb-8">
			<div class="flex items-center gap-4">
				<div class="flex h-16 w-16 items-center justify-center rounded-2xl bg-primary-fixed text-on-primary-fixed">
					<Building2 size={32} />
				</div>
				<div>
					<h1 class="text-headline-xl font-bold text-fg">{org.name}</h1>
					<p class="text-body-md text-on-surface-variant mt-1">@{org.slug}</p>
				</div>
			</div>
			<Button variant="outline" size="md" onclick={() => goto(`/organizations/${oid}/edit`)}>
				<Settings size={16} class="mr-1.5" />
				Edit
			</Button>
		</div>

		{#if org.description}
			<Card class="p-6 mb-6"><p class="text-body-md text-fg">{org.description}</p></Card>
		{/if}

		<div class="grid gap-6 md:grid-cols-2">
			<Card class="p-6">
				<div class="flex items-center gap-3 mb-4">
					<Users size={20} class="text-primary" />
					<h2 class="text-headline-md font-semibold text-fg">Members ({members.length})</h2>
				</div>
				<div class="space-y-3">
					{#each members as m}
						<div class="flex items-center justify-between py-2 border-b border-outline-variant/60 last:border-0">
							<span class="text-body-md text-fg">{m.user_id.slice(0,8)}...</span>
							<span class="rounded-md bg-surface-container-low px-2 py-0.5 text-label-sm text-on-surface-variant">{m.role}</span>
						</div>
					{/each}
				</div>
			</Card>

			<Card class="p-6">
				<div class="flex items-center gap-3 mb-4">
					<ExternalLink size={20} class="text-primary" />
					<h2 class="text-headline-md font-semibold text-fg">Links</h2>
				</div>
				<div class="space-y-3">
					{#if org.website_url}
						<a href={org.website_url} target="_blank" class="block text-body-md text-primary hover:underline">{org.website_url}</a>
					{:else}
						<p class="text-body-md text-on-surface-variant">No website</p>
					{/if}
				</div>
			</Card>
		</div>
	{/if}
</div>
