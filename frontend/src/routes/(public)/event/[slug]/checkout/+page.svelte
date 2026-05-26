<script lang="ts">
	import { onMount } from 'svelte';
	import { goto } from '$app/navigation';
	import { page } from '$app/stores';
	import { EVENTS, EVENT_BY_SLUG, AVAILABLE_TICKETS } from '$lib/graphql/queries/events';
	import { graphqlClient } from '$lib/graphql/client';
	import { createOrder, confirmOrder } from '$lib/services/orders';
	import Button from '$lib/components/ui/button.svelte';
	import Input from '$lib/components/ui/input.svelte';
	import Label from '$lib/components/ui/label.svelte';
	import Card from '$lib/components/ui/card.svelte';
	import { ArrowLeft, ShoppingCart } from 'lucide-svelte';

	let eventData = $state<Record<string, unknown> | null>(null);
	let tickets = $state<{ id: string; name: string; price: number; currency: string; max_per_order: number }[]>([]);
	let quantities = $state<Record<string, number>>({});
	let loading = $state(true);
	let submitting = $state(false);
	let error = $state<string | null>(null);
	let success = $state<string | null>(null);

	let email = $state(''); let name = $state(''); let phone = $state('');

	onMount(async () => {
		try {
			const eventsRes = await graphqlClient.query<{ events: { id: string; slug: string; organization_id: string }[] }>(EVENTS, { limit: 50 }).toPromise();
			const match = (eventsRes.data?.events ?? []).find((e: { slug: string }) => e.slug === $page.params.slug);
			if (!match) { error = 'Event not found'; loading = false; return; }

			const eventRes = await graphqlClient.query(EVENT_BY_SLUG, { organization_id: match.organization_id, slug: $page.params.slug }).toPromise();
			eventData = eventRes.data?.event_by_slug ?? null;

			if (eventData) {
				const ticketRes = await graphqlClient.query<{ available_tickets: { id: string; name: string; price: number; currency: string; max_per_order: number }[] }>(AVAILABLE_TICKETS, { event_id: (eventData as Record<string, string>).id }).toPromise();
				tickets = ticketRes.data?.available_tickets ?? [];
				tickets.forEach(t => { quantities[t.id] = 0; });
			}
		} catch (err) { error = 'Failed to load event'; }
		loading = false;
	});

	$: total = tickets.reduce((sum, t) => sum + (quantities[t.id] || 0) * Number(t.price), 0);
	$: hasItems = tickets.some(t => (quantities[t.id] || 0) > 0);

	async function handleSubmit(e: Event) {
		e.preventDefault(); error = null; submitting = true;
		try {
			const items = tickets.filter(t => (quantities[t.id] || 0) > 0).map(t => ({ ticket_id: t.id, quantity: quantities[t.id] }));
			const order = await createOrder({
				event_id: (eventData as Record<string, string>).id,
				customer_email: email, customer_name: name, customer_phone: phone || null,
				items,
			});
			if (!order) { error = 'Failed to create order'; submitting = false; return; }
			await confirmOrder(order.id);
			success = `Order #${order.order_number} confirmed!`;
		} catch (err) { error = err instanceof Error ? err.message : 'Checkout failed'; }
		submitting = false;
	}
</script>

<div class="mx-auto max-w-2xl px-6 py-8">
	<button onclick={() => goto(`/event/${$page.params.slug}`)} class="flex items-center gap-2 text-body-md text-on-surface-variant hover:text-fg mb-6 transition-colors"><ArrowLeft size={18} /> Back to event</button>

	{#if loading}<div class="h-64 rounded-xl bg-surface-container animate-pulse" />
	{:else if success}
		<div class="rounded-2xl border border-primary-fixed bg-primary-fixed/20 p-12 text-center animate-scale-in">
			<div class="mx-auto flex h-16 w-16 items-center justify-center rounded-2xl bg-primary text-on-primary mb-4"><ShoppingCart size={32} /></div>
			<h2 class="text-headline-xl font-bold text-fg mb-2">Order Confirmed!</h2>
			<p class="text-body-lg text-on-surface-variant mb-2">{success}</p>
			<Button variant="primary" size="lg" class="mt-4" onclick={() => goto('/')}>Back to Events</Button>
		</div>
	{:else if error}
		<div class="rounded-xl border border-error-container/50 bg-error-container/10 p-8 text-center"><p class="text-body-lg text-error">{error}</p><Button variant="outline" size="lg" class="mt-4" onclick={() => goto('/')}>Go Home</Button></div>
	{:else}
		<h1 class="text-headline-xl font-bold text-fg mb-2">Checkout</h1>
		<p class="text-body-md text-on-surface-variant mb-8">{eventData ? (eventData as Record<string, string>).name : ''}</p>

		<Card class="p-6 mb-6">
			<h2 class="text-headline-md font-semibold text-fg mb-4">Tickets</h2>
			<div class="space-y-4">
				{#each tickets as t}
					<div class="flex items-center justify-between py-3 border-b border-outline-variant/30 last:border-0">
						<div><p class="text-body-md font-semibold text-fg">{t.name}</p><p class="text-label-sm text-on-surface-variant">{t.currency === 'INR' ? '₹' : '$'}{t.price} each</p></div>
						<div class="flex items-center gap-3">
							<button class="flex h-8 w-8 items-center justify-center rounded-lg border border-outline-variant text-fg hover:bg-surface-container-low" onclick={() => { if ((quantities[t.id] || 0) > 0) quantities[t.id]--; }}>-</button>
							<span class="w-8 text-center text-body-md font-semibold text-fg">{quantities[t.id] || 0}</span>
							<button class="flex h-8 w-8 items-center justify-center rounded-lg border border-outline-variant text-fg hover:bg-surface-container-low" onclick={() => { if ((quantities[t.id] || 0) < (t.max_per_order || 10)) quantities[t.id] = (quantities[t.id] || 0) + 1; }}>+</button>
						</div>
					</div>
				{/each}
			</div>
			<div class="flex justify-between items-center mt-4 pt-4 border-t border-outline-variant/60">
				<span class="text-headline-md font-semibold text-fg">Total</span>
				<span class="text-headline-lg font-bold text-primary">${total.toFixed(2)}</span>
			</div>
		</Card>

		<Card class="p-6">
			<h2 class="text-headline-md font-semibold text-fg mb-4">Your Details</h2>
			<form onsubmit={handleSubmit} class="space-y-4">
				{#if error}<div class="rounded-lg border border-error-container/50 bg-error-container/10 p-3"><p class="text-body-md text-error">{error}</p></div>{/if}
				<div class="space-y-1.5"><Label for="name">Full Name</Label><Input id="name" bind:value={name} required /></div>
				<div class="space-y-1.5"><Label for="email">Email</Label><Input id="email" type="email" bind:value={email} required /></div>
				<div class="space-y-1.5"><Label for="phone">Phone</Label><Input id="phone" type="tel" bind:value={phone} /></div>
				<Button type="submit" variant="primary" size="xl" class="w-full" disabled={!hasItems} isLoading={submitting}>
					{hasItems ? `Pay $${total.toFixed(2)}` : 'Select tickets'}
				</Button>
			</form>
		</Card>
	{/if}
</div>
