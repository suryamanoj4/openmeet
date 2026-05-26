<script lang="ts">
	import { onMount } from 'svelte';
	import { goto } from '$app/navigation';
	import { page } from '$app/stores';
	import { EVENTS, EVENT_BY_SLUG, EVENT_TICKETS } from '$lib/graphql/queries/events';
	import { graphqlClient } from '$lib/graphql/client';
	import { ambientAuth } from '$lib/ambient-auth.svelte';
	import Button from '$lib/components/ui/button.svelte';
	import Card from '$lib/components/ui/card.svelte';
	import { Calendar, MapPin, Globe, Clock, Users } from 'lucide-svelte';

	let eventData = $state<Record<string, unknown> | null>(null);
	let tickets = $state<{ id: string; name: string; price: number; currency: string; quantity: number; sold_quantity: number }[]>([]);
	let loading = $state(true);
	let error = $state<string | null>(null);

	onMount(async () => {
		try {
			const eventsRes = await graphqlClient.query<{ events: { id: string; name: string; slug: string; organization_id: string }[] }>(EVENTS, { limit: 50 }).toPromise();
			const allEvents = eventsRes.data?.events ?? [];
			const match = allEvents.find((e: { slug: string }) => e.slug === $page.params.slug);
			if (!match) { error = 'Event not found'; loading = false; return; }

			const eventRes = await graphqlClient.query(EVENT_BY_SLUG, { organization_id: match.organization_id, slug: $page.params.slug }).toPromise();
			eventData = eventRes.data?.event_by_slug ?? null;

			if (eventData) {
				const ticketRes = await graphqlClient.query(EVENT_TICKETS, { event_id: (eventData as Record<string, string>).id }).toPromise();
				tickets = ticketRes.data?.event_tickets ?? [];
			}
		} catch (err) { error = 'Failed to load event'; }
		loading = false;
	});

	function formatDate(d: string) { return new Date(d).toLocaleDateString('en-US', { weekday: 'long', month: 'long', day: 'numeric', year: 'numeric', hour: 'numeric', minute: '2-digit' }); }

	function handleGetTickets() {
		if (!eventData) return;
		if (ambientAuth.isAuthenticated) goto(`/event/${$page.params.slug}/checkout`);
		else ambientAuth.requireAuth({ kind: 'get-tickets', label: 'Get tickets', execute: () => goto(`/event/${$page.params.slug}/checkout`) });
	}
</script>

<div class="mx-auto max-w-4xl px-6 py-8">
	{#if loading}<div class="h-96 rounded-2xl bg-surface-container animate-pulse"></div>
	{:else if error}<div class="text-center py-16"><p class="text-body-lg text-on-surface-variant">{error}</p></div>
	{:else if eventData}
		{@const e = eventData as Record<string, string>}

		{#if e.cover_image_url}
			<div class="aspect-[2/1] w-full rounded-2xl overflow-hidden mb-8"><img src={e.cover_image_url} alt={e.name} class="w-full h-full object-cover" /></div>
		{/if}

		<div class="mb-6">
			<span class="rounded-md bg-primary-fixed px-3 py-1 text-label-sm font-semibold text-on-primary-fixed">{e.event_type}</span>
			<h1 class="text-headline-xl font-bold text-fg mt-3">{e.name}</h1>
		</div>

		<div class="grid gap-3 sm:grid-cols-2 lg:grid-cols-4 mb-8">
			<Card class="p-4 flex items-center gap-3"><Calendar size={18} class="text-primary shrink-0" /><div><p class="text-label-sm text-on-surface-variant">Start</p><p class="text-body-md font-semibold text-fg">{formatDate(e.start_date)}</p></div></Card>
			<Card class="p-4 flex items-center gap-3"><Clock size={18} class="text-primary shrink-0" /><div><p class="text-label-sm text-on-surface-variant">End</p><p class="text-body-md font-semibold text-fg">{formatDate(e.end_date)}</p></div></Card>
			<Card class="p-4 flex items-center gap-3">
				{#if e.is_online === 'true'}<Globe size={18} class="text-primary shrink-0" />{:else}<MapPin size={18} class="text-primary shrink-0" />{/if}
				<div><p class="text-label-sm text-on-surface-variant">Location</p><p class="text-body-md font-semibold text-fg">{e.venue_city || (e.is_online === 'true' ? 'Online' : 'TBD')}</p></div>
			</Card>
			<Card class="p-4 flex items-center gap-3"><Users size={18} class="text-primary shrink-0" /><div><p class="text-label-sm text-on-surface-variant">Capacity</p><p class="text-body-md font-semibold text-fg">{e.max_attendees || 'Unlimited'}</p></div></Card>
		</div>

		{#if e.description}
			<Card class="p-6 mb-8"><p class="text-body-md text-fg whitespace-pre-line">{e.description}</p></Card>
		{/if}

		<div class="rounded-2xl border border-outline-variant bg-surface-container-lowest p-8 text-center">
			<h2 class="text-headline-lg font-semibold text-fg mb-6">Get Your Tickets</h2>
			{#if tickets.length > 0}
				<div class="space-y-3 mb-6 max-w-md mx-auto">
					{#each tickets as t}
						<Card class="p-4 flex items-center justify-between">
							<div><p class="text-headline-md font-semibold text-fg">{t.name}</p><p class="text-body-md text-on-surface-variant">{t.quantity - t.sold_quantity} remaining</p></div>
							<p class="text-headline-md font-bold text-primary">{t.currency === 'INR' ? '₹' : '$'}{t.price}</p>
						</Card>
					{/each}
				</div>
			{/if}
			<Button variant="primary" size="xl" onclick={handleGetTickets}>Get Tickets</Button>
		</div>
	{/if}
</div>
