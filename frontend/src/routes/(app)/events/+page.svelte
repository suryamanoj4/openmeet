<script lang="ts">
	import { onMount } from 'svelte';
	import { goto } from '$app/navigation';
	import { listEvents } from '$lib/services/events';
	import Button from '$lib/components/ui/button.svelte';
	import Card from '$lib/components/ui/card.svelte';
	import { Calendar, Plus, ArrowRight, Globe, MapPin } from 'lucide-svelte';
	import type { Event } from '$lib/graphql/types';

	let events = $state<Event[]>([]);
	let loading = $state(true);
	let filter = $state<'all' | 'draft' | 'published'>('all');

	onMount(async () => {
		events = await listEvents();
		loading = false;
	});

	$: filtered = filter === 'all' ? events : events.filter(e => e.status === filter);

	function formatDate(d: string) {
		return new Date(d).toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });
	}
</script>

<div class="mx-auto max-w-7xl px-6 py-8">
	<div class="flex items-center justify-between mb-8">
		<div>
			<h1 class="text-headline-xl font-bold text-fg">Events</h1>
			<p class="text-body-md text-on-surface-variant mt-1">{events.length} total events</p>
		</div>
		<Button variant="primary" size="lg" onclick={() => goto('/events/new')}>
			<Plus size={18} class="mr-1.5" /> New Event
		</Button>
	</div>

	<div class="flex gap-2 mb-6">
		{#each ['all', 'draft', 'published'] as f}
			<button class="px-4 py-2 rounded-lg text-label-md font-semibold transition-colors {filter === f ? 'bg-primary text-on-primary' : 'bg-surface-container-low text-on-surface-variant hover:bg-surface-container'}" onclick={() => filter = f as typeof filter}>
				{f.charAt(0).toUpperCase() + f.slice(1)}
			</button>
		{/each}
	</div>

	{#if loading}
		<div class="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">{#each [1,2,3] as _}<div class="h-48 rounded-xl bg-surface-container animate-pulse" />{/each}</div>
	{:else if filtered.length === 0}
		<div class="rounded-xl border border-outline-variant bg-surface-container-lowest p-16 text-center">
			<Calendar size={40} class="mx-auto text-on-surface-variant/40 mb-4" />
			<h3 class="text-headline-md font-semibold text-fg">No events found</h3>
			<Button variant="primary" size="lg" class="mt-6" onclick={() => goto('/events/new')}>Create Event</Button>
		</div>
	{:else}
		<div class="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
			{#each filtered as event}
				<Card class="cursor-pointer hover:shadow-md transition-all" onclick={() => goto(`/events/${event.id}`)}>
					{#if event.cover_image_url}
						<div class="aspect-video w-full overflow-hidden rounded-t-xl"><img src={event.cover_image_url} alt={event.name} class="w-full h-full object-cover" /></div>
					{/if}
					<div class="p-5 space-y-3">
						<div class="flex items-center justify-between">
							<span class="rounded-md px-2 py-0.5 text-label-sm font-semibold {event.status === 'published' ? 'bg-primary-fixed text-on-primary-fixed' : 'bg-surface-container-high text-on-surface-variant'}">{event.status}</span>
							<span class="text-label-sm text-on-surface-variant">{event.event_type}</span>
						</div>
						<h3 class="text-headline-md font-semibold text-fg leading-snug">{event.name}</h3>
						<div class="flex items-center gap-3 text-body-md text-on-surface-variant">
							<Calendar size={14} /><span>{formatDate(event.start_date)}</span>
							{event.venue_city ? <><MapPin size={14} /><span>{event.venue_city}</span></> : null}
							{event.is_online ? <Globe size={14} /> : null}
						</div>
						<div class="flex items-center justify-between pt-1">
							<span class="text-body-md text-on-surface-variant">{event.venue_city || (event.is_online ? 'Online' : 'TBD')}</span>
							<ArrowRight size={16} class="text-on-surface-variant" />
						</div>
					</div>
				</Card>
			{/each}
		</div>
	{/if}
</div>
