<script lang="ts">
	import { onMount } from 'svelte';
	import { goto } from '$app/navigation';
	import { page } from '$app/stores';
	import { PUBLIC_EVENT } from '$lib/graphql/queries/events';
	import { graphqlClient } from '$lib/graphql/client';
	import { ambientAuth } from '$lib/ambient-auth.svelte';
	import EventPageRenderer from '$lib/components/event-page-renderer.svelte';
	import Button from '$lib/components/ui/button.svelte';
	import Card from '$lib/components/ui/card.svelte';
	import { normalizeEventPageBlocks } from '$lib/event-page';
	import type { Event, Ticket } from '$lib/graphql/types';
	import { Calendar, Clock, Globe, MapPin, Users } from 'lucide-svelte';

	interface PublicEventResponse {
		public_event: {
			event: Event;
			page: { blocks: unknown; is_published: boolean };
			tickets: Ticket[];
		} | null;
	}

	let result = $state<PublicEventResponse['public_event']>(null);
	let loading = $state(true);
	let error = $state<string | null>(null);

	onMount(async () => {
		const response = await graphqlClient.query<PublicEventResponse>(PUBLIC_EVENT, {
			id: $page.params.id,
			slug: $page.params.slug
		}).toPromise();
		if (response.error) error = response.error.message;
		else if (!response.data?.public_event) error = 'Published event not found';
		else result = response.data.public_event;
		loading = false;
	});

	function formatDate(value: string) {
		return new Date(value).toLocaleString(undefined, {
			weekday: 'short',
			year: 'numeric',
			month: 'long',
			day: 'numeric',
			hour: 'numeric',
			minute: '2-digit'
		});
	}

	function getTickets() {
		const target = `/event/${$page.params.slug}/checkout`;
		if (ambientAuth.isAuthenticated) goto(target);
		else ambientAuth.requireAuth({ kind: 'get-tickets', label: 'Get tickets', execute: () => goto(target) });
	}
</script>

<div class="mx-auto max-w-5xl px-6 py-8">
	{#if loading}
		<div class="h-96 animate-pulse rounded-2xl bg-surface-container"></div>
	{:else if error || !result}
		<div class="py-20 text-center text-body-lg text-on-surface-variant">{error || 'Event not found'}</div>
	{:else}
		{@const event = result.event}
		{#if event.cover_image_url}<img class="mb-8 aspect-[2/1] w-full rounded-2xl object-cover" src={event.cover_image_url} alt={event.name} />{/if}
		<header class="mb-8">
			<span class="rounded-md bg-primary-fixed px-3 py-1 text-label-sm font-semibold text-on-primary-fixed">{event.event_type}</span>
			<h1 class="mt-3 text-headline-xl font-bold text-fg">{event.name}</h1>
		</header>
		<div class="mb-10 grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
			<Card class="flex items-center gap-3 p-4"><Calendar size={18} class="text-primary" /><div><p class="text-label-sm text-on-surface-variant">Start</p><p class="font-semibold">{formatDate(event.start_date)}</p></div></Card>
			<Card class="flex items-center gap-3 p-4"><Clock size={18} class="text-primary" /><div><p class="text-label-sm text-on-surface-variant">End</p><p class="font-semibold">{formatDate(event.end_date)}</p></div></Card>
			<Card class="flex items-center gap-3 p-4">{#if event.is_online}<Globe size={18} class="text-primary" />{:else}<MapPin size={18} class="text-primary" />{/if}<div><p class="text-label-sm text-on-surface-variant">Location</p><p class="font-semibold">{event.venue_city || (event.is_online ? 'Online' : 'TBD')}</p></div></Card>
			<Card class="flex items-center gap-3 p-4"><Users size={18} class="text-primary" /><div><p class="text-label-sm text-on-surface-variant">Capacity</p><p class="font-semibold">{event.max_attendees ?? 'Unlimited'}</p></div></Card>
		</div>

		<EventPageRenderer blocks={normalizeEventPageBlocks(result.page.blocks)} />

		<section id="tickets" class="mt-12 rounded-2xl border border-outline-variant p-8 text-center">
			<h2 class="text-headline-lg font-semibold">Get Your Tickets</h2>
			{#if result.tickets.length}
				<div class="mx-auto my-6 max-w-lg space-y-3">
					{#each result.tickets as ticket}
						<Card class="flex items-center justify-between p-4"><div class="text-left"><p class="font-semibold">{ticket.name}</p><p class="text-on-surface-variant">{ticket.quantity - ticket.sold_quantity} remaining</p></div><strong class="text-primary">{ticket.currency === 'INR' ? '₹' : '$'}{ticket.price}</strong></Card>
					{/each}
				</div>
				<Button variant="primary" size="xl" onclick={getTickets}>Get Tickets</Button>
			{:else}
				<p class="mt-4 text-on-surface-variant">Tickets are not available yet.</p>
			{/if}
		</section>
	{/if}
</div>
