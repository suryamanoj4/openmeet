<script lang="ts">
	import { onMount } from 'svelte';
	import { goto } from '$app/navigation';
	import { page } from '$app/stores';
	import { getEvent, updateEvent } from '$lib/services/events';
	import { listOrganizations } from '$lib/services/organizations';
	import Button from '$lib/components/ui/button.svelte';
	import Input from '$lib/components/ui/input.svelte';
	import Label from '$lib/components/ui/label.svelte';
	import Card from '$lib/components/ui/card.svelte';
	import CardHeader from '$lib/components/ui/card-header.svelte';
	import CardTitle from '$lib/components/ui/card-title.svelte';
	import CardContent from '$lib/components/ui/card-content.svelte';
	import { ArrowLeft } from 'lucide-svelte';
	import type { Organization } from '$lib/graphql/types';

	let name = $state(''); let slug = $state(''); let description = $state('');
	let event_type = $state('conference'); let venue_city = $state(''); let is_online = $state(false);
	let cover_image_url = $state(''); let organization_id = $state<string | undefined>(undefined);
	let orgs = $state<Organization[]>([]);
	let error = $state<string | null>(null); let saving = $state(false); let loading = $state(true);

	onMount(async () => {
		const [event, orgList] = await Promise.all([getEvent($page.params.id), listOrganizations()]);
		orgs = orgList;
		if (event) {
			name = event.name; slug = event.slug; description = event.description || '';
			event_type = event.event_type; venue_city = event.venue_city || '';
			is_online = event.is_online; cover_image_url = event.cover_image_url || '';
			organization_id = event.organization_id || undefined;
		}
		loading = false;
	});

	async function handleSubmit(e: Event) {
		e.preventDefault(); error = null; saving = true;
		try {
			await updateEvent($page.params.id, {
				name, slug, description: description || null, event_type,
				venue_city: venue_city || null, is_online, cover_image_url: cover_image_url || null,
			});
			goto(`/events/${$page.params.id}`);
		} catch (err) { error = err instanceof Error ? err.message : 'Failed'; } finally { saving = false; }
	}
</script>

<div class="mx-auto max-w-2xl px-6 py-8">
	<button onclick={() => goto(`/events/${$page.params.id}`)} class="flex items-center gap-2 text-body-md text-on-surface-variant hover:text-fg mb-6 transition-colors"><ArrowLeft size={18} /> Back</button>
	<Card>
		<CardHeader><CardTitle>Edit Event</CardTitle></CardHeader>
		<CardContent>
			{#if loading}<div class="h-48 animate-pulse rounded-lg bg-surface-container" />
			{:else}
				<form onsubmit={handleSubmit} class="space-y-5">
					{#if error}<div class="rounded-lg border border-error-container/50 bg-error-container/10 p-3"><p class="text-body-md text-error">{error}</p></div>{/if}
					<div class="space-y-1.5"><Label for="name">Name</Label><Input id="name" bind:value={name} required /></div>
					<div class="space-y-1.5"><Label for="slug">Slug</Label><Input id="slug" bind:value={slug} required /></div>
					<div class="space-y-1.5"><Label for="desc">Description</Label><textarea id="desc" bind:value={description} class="flex min-h-[80px] w-full rounded-lg border border-input bg-surface-container-lowest px-3 py-2 text-body-md focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring" /></div>
					<div class="grid grid-cols-2 gap-4">
						<div class="space-y-1.5"><Label for="type">Type</Label><select id="type" bind:value={event_type} class="flex h-10 w-full rounded-lg border border-input bg-surface-container-lowest px-3 text-body-md"><option value="conference">Conference</option><option value="workshop">Workshop</option><option value="meetup">Meetup</option><option value="webinar">Webinar</option><option value="hackathon">Hackathon</option></select></div>
						<div class="space-y-1.5"><Label for="org">Organization</Label><select id="org" bind:value={organization_id} class="flex h-10 w-full rounded-lg border border-input bg-surface-container-lowest px-3 text-body-md"><option value={undefined}>Personal event</option>{#each orgs as org}<option value={org.id}>{org.name}</option>{/each}</select></div>
					</div>
					<div class="grid grid-cols-2 gap-4">
						<div class="space-y-1.5"><Label for="city">City</Label><Input id="city" bind:value={venue_city} /></div>
						<div class="space-y-1.5 flex items-end pb-2"><label class="flex items-center gap-2 cursor-pointer"><input type="checkbox" bind:checked={is_online} class="w-4 h-4 rounded border-outline-variant text-primary" /><span class="text-body-md text-fg">Online event</span></label></div>
					</div>
					<div class="space-y-1.5"><Label for="cover">Cover Image URL</Label><Input id="cover" bind:value={cover_image_url} /></div>
					<div class="flex gap-3 pt-2"><Button type="submit" variant="primary" size="lg" isLoading={saving}>Save</Button><Button type="button" variant="outline" size="lg" onclick={() => goto(`/events/${$page.params.id}`)}>Cancel</Button></div>
				</form>
			{/if}
		</CardContent>
	</Card>
</div>
