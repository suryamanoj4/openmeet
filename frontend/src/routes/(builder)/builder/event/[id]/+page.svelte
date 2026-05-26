<script lang="ts">
	import { onMount } from 'svelte';
	import { goto } from '$app/navigation';
	import { page } from '$app/stores';
	import { getEvent, getEventTickets } from '$lib/services/events';
	import { createTicket, deleteTicket } from '$lib/graphql/queries/tickets';
	import { graphqlClient } from '$lib/graphql/client';
	import Button from '$lib/components/ui/button.svelte';
	import Input from '$lib/components/ui/input.svelte';
	import Label from '$lib/components/ui/label.svelte';
	import Card from '$lib/components/ui/card.svelte';
	import { ArrowLeft, Plus, Trash2, Layout, Eye, Ticket } from 'lucide-svelte';
	import type { Event } from '$lib/graphql/types';

	let event = $state<Event | null>(null);
	let tickets = $state<{ id: string; name: string; price: number; currency: string; quantity: number }[]>([]);
	let loading = $state(true);
	let activeTab = $state<'blocks' | 'tickets'>('tickets');

	// Ticket form
	let newTicketName = $state(''); let newTicketPrice = $state(0); let newTicketQty = $state(100);
	let ticketError = $state<string | null>(null); let savingTicket = $state(false);

	// Page blocks (lite builder)
	type Block = { type: string; title: string; content: string; visible: boolean };
	let blocks = $state<Block[]>([]);
	let blockTypes = ['Hero', 'About', 'Schedule', 'Speakers', 'Venue', 'FAQs', 'CTA'];

	onMount(async () => {
		const id = $page.params.id;
		event = await getEvent(id);
		if (event) tickets = await getEventTickets(id);
		loading = false;
	});

	async function addTicket() {
		if (!newTicketName) return; ticketError = null; savingTicket = true;
		try {
			const r = await graphqlClient.mutation<{ create_ticket: { id: string; name: string } }>(createTicket, {
				input: { event_id: $page.params.id, name: newTicketName, price: newTicketPrice, quantity: newTicketQty, currency: 'USD', sort_order: tickets.length }
			}).toPromise();
			if (r.data?.create_ticket) {
				tickets = [...tickets, { id: r.data.create_ticket.id, name: newTicketName, price: newTicketPrice, currency: 'USD', quantity: newTicketQty }];
				newTicketName = ''; newTicketPrice = 0; newTicketQty = 100;
			} else ticketError = 'Failed to create ticket';
		} catch (err) { ticketError = err instanceof Error ? err.message : 'Failed'; }
		savingTicket = false;
	}

	async function removeTicket(id: string) {
		await graphqlClient.mutation(DELETE_TICKET, { id }).toPromise();
		tickets = tickets.filter(t => t.id !== id);
	}

	function addBlock(type: string) {
		const defaults: Record<string, Block> = {
			Hero: { type, title: 'Hero Section', content: 'Headline and CTA', visible: true },
			About: { type, title: 'About', content: 'Event description goes here...', visible: true },
			Schedule: { type, title: 'Schedule', content: 'Timeline and agenda', visible: true },
			Speakers: { type, title: 'Speakers', content: 'Speaker name, bio, photo', visible: true },
			Venue: { type, title: 'Venue', content: 'Location details and map', visible: true },
			FAQs: { type, title: 'FAQs', content: 'Frequently asked questions', visible: true },
			CTA: { type, title: 'Call to Action', content: 'Get tickets now!', visible: true },
		};
		blocks = [...blocks, defaults[type] || { type, title: type, content: '', visible: true }];
	}

	function removeBlock(idx: number) { blocks = blocks.filter((_, i) => i !== idx); }
</script>

<div class="mx-auto max-w-6xl px-6 py-8">
	<button onclick={() => goto(`/events/${$page.params.id}`)} class="flex items-center gap-2 text-body-md text-on-surface-variant hover:text-fg mb-6 transition-colors"><ArrowLeft size={18} /> Back to event</button>

	{#if loading}<div class="h-64 rounded-xl bg-surface-container animate-pulse" />
	{:else if !event}<div class="text-center py-16"><p class="text-body-lg text-on-surface-variant">Event not found</p></div>
	{:else}
		<div class="flex items-center gap-3 mb-8">
			<div class="flex h-12 w-12 items-center justify-center rounded-xl bg-primary-fixed text-primary"><Layout size={24} /></div>
			<div><h1 class="text-headline-xl font-bold text-fg">Event Builder</h1><p class="text-body-md text-on-surface-variant">{event.name}</p></div>
		</div>

		<div class="flex gap-2 mb-6">
			<button class="px-4 py-2 rounded-lg text-label-md font-semibold transition-colors {activeTab === 'tickets' ? 'bg-primary text-on-primary' : 'bg-surface-container-low text-on-surface-variant'}" onclick={() => activeTab = 'tickets'}><Ticket size={16} class="inline mr-1" />Tickets</button>
			<button class="px-4 py-2 rounded-lg text-label-md font-semibold transition-colors {activeTab === 'blocks' ? 'bg-primary text-on-primary' : 'bg-surface-container-low text-on-surface-variant'}" onclick={() => activeTab = 'blocks'}><Layout size={16} class="inline mr-1" />Page Blocks</button>
			<button class="px-4 py-2 rounded-lg text-label-md font-semibold transition-colors {activeTab === 'preview' ? 'bg-primary text-on-primary' : 'bg-surface-container-low text-on-surface-variant'}" onclick={() => activeTab = 'preview'}><Eye size={16} class="inline mr-1" />Preview</button>
		</div>

		{#if activeTab === 'tickets'}
			<Card class="p-6">
				<h2 class="text-headline-md font-semibold text-fg mb-4">Ticket Types</h2>
				{#if tickets.length > 0}
					<div class="space-y-3 mb-6">
						{#each tickets as t}
							<div class="flex items-center justify-between p-3 rounded-lg border border-outline-variant">
								<div><p class="text-body-md font-semibold text-fg">{t.name}</p><p class="text-label-sm text-on-surface-variant">{t.currency === 'INR' ? '₹' : '$'}{t.price} &middot; {t.quantity} available</p></div>
								<button onclick={() => removeTicket(t.id)} class="text-on-surface-variant hover:text-error transition-colors"><Trash2 size={16} /></button>
							</div>
						{/each}
					</div>
				{/if}
				<div class="border-t border-outline-variant/60 pt-4">
					<h3 class="text-label-md text-fg mb-3">Add Ticket Type</h3>
					{#if ticketError}<div class="rounded-lg border border-error-container/50 bg-error-container/10 p-3 mb-3"><p class="text-body-md text-error">{ticketError}</p></div>{/if}
					<div class="grid grid-cols-3 gap-3 mb-3">
						<div><Label for="tname">Name</Label><Input id="tname" bind:value={newTicketName} placeholder="General Admission" /></div>
						<div><Label for="tprice">Price</Label><Input id="tprice" type="number" bind:value={newTicketPrice} /></div>
						<div><Label for="tqty">Quantity</Label><Input id="tqty" type="number" bind:value={newTicketQty} /></div>
					</div>
					<Button variant="primary" size="sm" onclick={addTicket} isLoading={savingTicket}><Plus size={14} class="mr-1" />Add Ticket</Button>
				</div>
			</Card>

		{:else if activeTab === 'blocks'}
			<div class="grid gap-6 lg:grid-cols-[1fr_300px]">
				<div class="space-y-4">
					{#if blocks.length === 0}
						<Card class="p-12 text-center"><Layout size={40} class="mx-auto text-on-surface-variant/40 mb-4" /><p class="text-body-md text-on-surface-variant">No blocks yet. Add one from the panel.</p></Card>
					{:else}
						{#each blocks as block, i}
							<Card class="p-5">
								<div class="flex items-center justify-between mb-3">
									<div class="flex items-center gap-2"><span class="rounded-md bg-primary-fixed px-2 py-0.5 text-label-sm text-on-primary-fixed-variant">{block.type}</span><h3 class="text-headline-md font-semibold text-fg">{block.title}</h3></div>
									<button onclick={() => removeBlock(i)} class="text-on-surface-variant hover:text-error"><Trash2 size={16} /></button>
								</div>
								<textarea bind:value={block.content} class="w-full min-h-[80px] rounded-lg border border-input bg-surface-container-lowest px-3 py-2 text-body-md focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring" placeholder="Content..." />
							</Card>
						{/each}
					{/if}
				</div>
				<Card class="p-5 h-fit sticky top-24">
					<h3 class="text-label-md text-fg mb-3">Add Block</h3>
					<div class="space-y-2">
						{#each blockTypes as type}
							<button class="w-full text-left px-3 py-2 rounded-lg text-body-md text-on-surface-variant hover:bg-surface-container-low hover:text-fg transition-colors" onclick={() => addBlock(type)}>+ {type}</button>
						{/each}
					</div>
				</Card>
			</div>

		{:else if activeTab === 'preview'}
			<div class="space-y-6">
				{#if blocks.length === 0}
					<Card class="p-12 text-center"><p class="text-body-md text-on-surface-variant">No blocks to preview</p></Card>
				{:else}
					{#each blocks as block}
						<Card class="p-8">
							{#if block.type === 'Hero'}
								<div class="text-center py-12"><span class="rounded-full bg-primary-fixed px-4 py-1.5 text-label-sm text-on-primary-fixed-variant">{event.name}</span><h2 class="text-headline-xl font-bold text-fg mt-4">{block.content}</h2></div>
							{:else}
								<h3 class="text-headline-lg font-semibold text-fg mb-3">{block.title}</h3>
								<p class="text-body-md text-on-surface-variant whitespace-pre-line">{block.content}</p>
							{/if}
						</Card>
						{#if block.type === 'CTA'}
							<div class="text-center py-8"><Button variant="primary" size="xl">Get Tickets</Button></div>
						{/if}
					{/each}
				{/if}
			</div>
		{/if}
	{/if}
</div>
