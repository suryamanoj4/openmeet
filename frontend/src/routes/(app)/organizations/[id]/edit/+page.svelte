<script lang="ts">
	import { onMount } from 'svelte';
	import { goto } from '$app/navigation';
	import { page } from '$app/stores';
	import { getOrganization, updateOrganization } from '$lib/services/organizations';
	import Button from '$lib/components/ui/button.svelte';
	import Input from '$lib/components/ui/input.svelte';
	import Label from '$lib/components/ui/label.svelte';
	import Card from '$lib/components/ui/card.svelte';
	import CardHeader from '$lib/components/ui/card-header.svelte';
	import CardTitle from '$lib/components/ui/card-title.svelte';
	import CardContent from '$lib/components/ui/card-content.svelte';
	import { ArrowLeft } from 'lucide-svelte';

	let name = $state('');
	let slug = $state('');
	let description = $state('');
	let error = $state<string | null>(null);
	let saving = $state(false);
	let loading = $state(true);

	onMount(async () => {
		const org = await getOrganization($page.params.id);
		if (org) { name = org.name; slug = org.slug; description = org.description || ''; }
		loading = false;
	});

	async function handleSubmit(e: Event) {
		e.preventDefault();
		error = null; saving = true;
		try {
			await updateOrganization($page.params.id, { name, slug, description });
			goto(`/organizations/${$page.params.id}`);
		} catch (err) {
			error = err instanceof Error ? err.message : 'Failed to update';
		} finally { saving = false; }
	}
</script>

<div class="mx-auto max-w-2xl px-6 py-8">
	<button onclick={() => goto(`/organizations/${$page.params.id}`)} class="flex items-center gap-2 text-body-md text-on-surface-variant hover:text-fg mb-6 transition-colors">
		<ArrowLeft size={18} /> Back
	</button>
	<Card>
		<CardHeader><CardTitle>Edit Organization</CardTitle></CardHeader>
		<CardContent>
			{#if loading}
				<div class="h-48 animate-pulse rounded-lg bg-surface-container" />
			{:else}
				<form onsubmit={handleSubmit} class="space-y-5">
					{#if error}<div class="rounded-lg border border-error-container/50 bg-error-container/10 p-3"><p class="text-body-md text-error">{error}</p></div>{/if}
					<div class="space-y-1.5"><Label for="name">Name</Label><Input id="name" bind:value={name} required /></div>
					<div class="space-y-1.5"><Label for="slug">Slug</Label><Input id="slug" bind:value={slug} required /></div>
					<div class="space-y-1.5"><Label for="desc">Description</Label><textarea id="desc" bind:value={description} class="flex min-h-[100px] w-full rounded-lg border border-input bg-surface-container-lowest px-3 py-2 text-body-md focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring" /></div>
					<div class="flex gap-3 pt-2">
						<Button type="submit" variant="primary" size="lg" isLoading={saving}>Save</Button>
						<Button type="button" variant="outline" size="lg" onclick={() => goto(`/organizations/${$page.params.id}`)}>Cancel</Button>
					</div>
				</form>
			{/if}
		</CardContent>
	</Card>
</div>
