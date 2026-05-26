<script lang="ts">
	import { onMount } from 'svelte';
	import { goto } from '$app/navigation';
	import { page } from '$app/stores';
	import { getEvent, getEventTickets, deleteEvent } from '$lib/services/events';
	import Button from '$lib/components/ui/button.svelte';
	import Card from '$lib/components/ui/card.svelte';
	import { ArrowLeft, Calendar, MapPin, Globe, Clock, Users, Ticket, Trash2, Settings } from 'lucide-svelte';
	import type { Event } from '$lib/graphql/types';

	let event = $state<Event | null>(null);
	let tickets = $state<{ id: string; name: string; price: number; currency: string; quantity: number; sold_quantity: number }[]>([]);
	let loading = $state(true);
	let deleting = $state(false);

	onMount(async () => {
		const id = $page.params.id;
		event = await getEvent(id);
		if (event) tickets = await getEventTickets(id);
		loading = false;
	});

	async function handleDelete() {
		if (!confirm('Delete this event? This cannot be undone.')) return;
		deleting = true;
		await deleteEvent($page.params.id);
		goto('/events');
	}

	function formatDate(d: string) {
		return new Date(d).toLocaleDateString('en-US', { weekday: 'short', month: 'long', day: 'numeric', year: 'numeric', hour: 'numeric', minute: '2-digit' });
	}
</script>

<div class="mx-auto max-w-4xl px-6 py-8">
	<button onclick={() => goto('/events')} class="flex items-center gap-2 text-body-md text-on-surface-variant hover:text-fg mb-6 transition-colors"><ArrowLeft size={18} /> Events</button>

	{#if loading}<div class="h-64 rounded-xl bg-surface-container animate-pulse" />
	{:else if !event}<div class="text-center py-16"><p class="text-body-lg text-on-surface-variant">Event not found</p></div>
	{:else}
		{#if event.cover_image_url}
			<div class="aspect-[2/1] w-full rounded-2xl overflow-hidden mb-8"><img src={event.cover_image_url} alt={event.name} class="w-full h-full object-cover" /></div>
		{/if}

		<div class="flex items-start justify-between mb-6">
			<div>
				<div class="flex items-center gap-3 mb-2">
					<span class="rounded-md px-2.5 py-1 text-label-sm font-semibold {event.status === 'published' ? 'bg-primary-fixed text-on-primary-fixed' : 'bg-surface-container-high text-on-surface-variant'}">{event.status}</span>
					<span class="text-label-sm text-on-surface-variant">{event.event_type}</span>
					<span class="text-label-sm text-on-surface-variant">{event.visibility}</span>
				</div>
				<h1 class="text-headline-xl font-bold text-fg">{event.name}</h1>
			</div>
			<div class="flex gap-2">
				<Button variant="outline" size="sm" onclick={() => goto(`/events/${event.id}/edit`)}><Settings size={14} class="mr-1" />Edit</Button>
				<Button variant="destructive" size="sm" onclick={handleDelete} isLoading={deleting}><Trash2 size={14} class="mr-1" />Delete</Button>
			</div>
		</div>

		<div class="grid gap-4 sm:grid-cols-2 lg:grid-cols-4 mb-8">
			<Card class="p-4 flex items-center gap-3"><Calendar size={18} class="text-primary shrink-0" /><div><p class="text-label-sm text-on-surface-variant">Start</p><p class="text-body-md font-semibold text-fg">{formatDate(event.start_date)}</p></div></Card>
			<Card class="p-4 flex items-center gap-3"><Clock size={18} class="text-primary shrink-0" /><div><p class="text-label-sm text-on-surface-variant">End</p><p class="text-body-md font-semibold text-fg">{formatDate(event.end_date)}</p></div></Card>
			<Card class="p-4 flex items-center gap-3"><MapPin size={18} class="text-primary shrink-0" /><div><p class="text-label-sm text-on-surface-variant">Location</p><p class="text-body-md font-semibold text-fg">{event.venue_city || (event.is_online ? 'Online' : 'TBD')}</p></div></Card>
			<Card class="p-4 flex items-center gap-3"><Users size={18} class="text-primary shrink-0" /><div><p class="text-label-sm text-on-surface-variant">Capacity</p><p class="text-body-md font-semibold text-fg">{event.max_attendees ?? 'Unlimited'}</p></div></Card>
		</div>

		{#if event.description}
			<Card class="p-6 mb-8"><p class="text-body-md text-fg whitespace-pre-line">{event.description}</p></Card>
		{/if}

		<div class="mb-8">
			<div class="flex items-center justify-between mb-4">
				<h2 class="text-headline-lg font-semibold text-fg"><Ticket size={20} class="inline mr-2 text-primary" />Tickets</h2>
				<Button variant="outline" size="sm" onclick={() => goto(`/builder/event/${event.id}`)}>Manage Tickets</Button>
			</div>
			{#if tickets.length === 0}
				<Card class="p-6 text-center"><p class="text-body-md text-on-surface-variant">No tickets configured yet</p></Card>
			{:else}
				<div class="grid gap-3">
					{#each tickets as t}
						<Card class="p-4 flex items-center justify-between">
							<div><h3 class="text-headline-md font-semibold text-fg">{t.name}</h3><p class="text-body-md text-on-surface-variant">{t.sold_quantity} / {t.quantity} sold</p></div>
							<div class="text-right"><p class="text-headline-md font-bold text-primary">{t.currency === 'INR' ? '₹' : '$'}{t.price}</p></div>
						</Card>
					{/each}
				</div>
			{/if}
		</div>

		<div class="flex gap-3">
			<Button variant="primary" size="lg" onclick={() => goto(`/builder/event/${event.id}`)}>Open Page Builder</Button>
			<Button variant="outline" size="lg" onclick={() => goto(`/attendees?eventId=${event.id}`)}>View Attendees</Button>
		</div>
	{/if}
</div>
