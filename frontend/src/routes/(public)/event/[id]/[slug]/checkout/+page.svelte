<script lang="ts">
	import { onMount } from 'svelte';
	import { goto } from '$app/navigation';
	import { page } from '$app/stores';
	import { graphqlClient } from '$lib/graphql/client';
	import { PUBLIC_EVENT } from '$lib/graphql/queries/events';
	import { createOrder, createPaymentOrder, verifyPayment } from '$lib/services/orders';
	import Button from '$lib/components/ui/button.svelte';
	import Card from '$lib/components/ui/card.svelte';
	import Input from '$lib/components/ui/input.svelte';
	import Label from '$lib/components/ui/label.svelte';
	import type { Event, Ticket } from '$lib/graphql/types';
	import { ArrowLeft, ShoppingCart } from 'lucide-svelte';

	interface RazorpayResult {
		razorpay_payment_id: string;
		razorpay_order_id: string;
		razorpay_signature: string;
	}

	interface RazorpayConstructor {
		new(options: Record<string, unknown>): { open(): void; on(name: string, callback: (response: { error?: { description?: string } }) => void): void };
	}

	let event = $state<Event | null>(null);
	let tickets = $state<Ticket[]>([]);
	let quantities = $state<Record<string, number>>({});
	let loading = $state(true);
	let submitting = $state(false);
	let error = $state<string | null>(null);
	let success = $state<string | null>(null);
	let email = $state('');
	let name = $state('');
	let phone = $state('');

	let total = $derived(tickets.reduce((sum, ticket) => sum + (quantities[ticket.id] || 0) * Number(ticket.price), 0));
	let hasItems = $derived(tickets.some((ticket) => (quantities[ticket.id] || 0) > 0));

	onMount(async () => {
		const response = await graphqlClient.query<{ public_event: { event: Event; tickets: Ticket[] } | null }>(
			PUBLIC_EVENT,
			{ id: $page.params.id, slug: $page.params.slug }
		).toPromise();
		if (response.error) error = response.error.message;
		else if (!response.data?.public_event) error = 'Published event not found';
		else {
			event = response.data.public_event.event;
			tickets = response.data.public_event.tickets;
			for (const ticket of tickets) quantities[ticket.id] = 0;
		}
		loading = false;
	});

	async function loadRazorpay(): Promise<RazorpayConstructor> {
		const existing = (window as unknown as { Razorpay?: RazorpayConstructor }).Razorpay;
		if (existing) return existing;
		await new Promise<void>((resolve, reject) => {
			const script = document.createElement('script');
			script.src = 'https://checkout.razorpay.com/v1/checkout.js';
			script.onload = () => resolve();
			script.onerror = () => reject(new Error('Unable to load the payment provider'));
			document.head.appendChild(script);
		});
		const loaded = (window as unknown as { Razorpay?: RazorpayConstructor }).Razorpay;
		if (!loaded) throw new Error('Payment provider did not initialize');
		return loaded;
	}

	async function handleSubmit(submitEvent: SubmitEvent) {
		submitEvent.preventDefault();
		if (!event || !hasItems) return;
		error = null;
		submitting = true;
		try {
			const order = await createOrder({
				event_id: event.id,
				customer_email: email,
				customer_name: name,
				customer_phone: phone || null,
				items: tickets
					.filter((ticket) => (quantities[ticket.id] || 0) > 0)
					.map((ticket) => ({ ticket_id: ticket.id, quantity: quantities[ticket.id] }))
			});
			if (Number(order.total_amount) === 0 || order.payment_status === 'free') {
				success = `Order #${order.order_number} confirmed.`;
				return;
			}

			const payment = await createPaymentOrder(order.id);
			const Razorpay = await loadRazorpay();
			await new Promise<void>((resolve, reject) => {
				const checkout = new Razorpay({
					key: payment.provider_key_id,
					order_id: payment.provider_order_id,
					amount: payment.amount,
					currency: payment.currency,
					name: event?.name,
					prefill: { name, email, contact: phone },
					handler: async (result: RazorpayResult) => {
						try {
							const verification = await verifyPayment({
								order_id: order.id,
								provider_payment_id: result.razorpay_payment_id,
								provider_order_id: result.razorpay_order_id,
								signature: result.razorpay_signature
							});
							if (!verification.success) throw new Error(verification.message);
							success = `Order #${order.order_number} confirmed.`;
							resolve();
						} catch (verificationError) {
							reject(verificationError);
						}
					},
					modal: { ondismiss: () => reject(new Error('Payment was cancelled')) }
				});
				checkout.on('payment.failed', (response) => reject(new Error(response.error?.description || 'Payment failed')));
				checkout.open();
			});
		} catch (submitError) {
			error = submitError instanceof Error ? submitError.message : 'Checkout failed';
		} finally {
			submitting = false;
		}
	}
</script>

<div class="mx-auto max-w-2xl px-6 py-8">
	<button onclick={() => goto(`/event/${$page.params.id}/${$page.params.slug}`)} class="mb-6 flex items-center gap-2 text-on-surface-variant"><ArrowLeft size={18} /> Back to event</button>
	{#if loading}
		<div class="h-64 animate-pulse rounded-xl bg-surface-container"></div>
	{:else if success}
		<div class="rounded-2xl border border-primary-fixed bg-primary-fixed/20 p-12 text-center"><ShoppingCart class="mx-auto mb-4 text-primary" size={48} /><h1 class="text-headline-xl font-bold">Order Confirmed</h1><p class="mt-2 text-on-surface-variant">{success}</p><Button class="mt-6" onclick={() => goto('/')}>Back to Events</Button></div>
	{:else if !event}
		<p class="py-16 text-center text-error">{error || 'Event not found'}</p>
	{:else}
		<h1 class="text-headline-xl font-bold">Checkout</h1>
		<p class="mb-8 text-on-surface-variant">{event.name}</p>
		{#if error}<div class="mb-4 rounded-lg border border-error-container bg-error-container/10 p-3 text-error">{error}</div>{/if}
		<form class="space-y-6" onsubmit={handleSubmit}>
			<Card class="space-y-4 p-6">
				<h2 class="font-semibold">Tickets</h2>
				{#each tickets as ticket}
					<div class="flex items-center justify-between border-b border-outline-variant/40 py-3">
						<div><p class="font-semibold">{ticket.name}</p><p class="text-on-surface-variant">{ticket.currency} {ticket.price}</p></div>
						<div class="flex items-center gap-3"><button type="button" onclick={() => quantities[ticket.id] = Math.max(0, (quantities[ticket.id] || 0) - 1)}>-</button><span>{quantities[ticket.id] || 0}</span><button type="button" onclick={() => quantities[ticket.id] = Math.min(ticket.max_per_order, (quantities[ticket.id] || 0) + 1)}>+</button></div>
					</div>
				{/each}
				<p class="text-right text-headline-md font-bold">Total: {tickets[0]?.currency || 'USD'} {total.toFixed(2)}</p>
			</Card>
			<Card class="space-y-4 p-6"><h2 class="font-semibold">Your details</h2><div><Label for="buyer-name">Full name</Label><Input id="buyer-name" bind:value={name} required /></div><div><Label for="buyer-email">Email</Label><Input id="buyer-email" type="email" bind:value={email} required /></div><div><Label for="buyer-phone">Phone</Label><Input id="buyer-phone" type="tel" bind:value={phone} /></div><Button type="submit" class="w-full" size="xl" disabled={!hasItems} isLoading={submitting}>{hasItems ? `Continue · ${total.toFixed(2)}` : 'Select tickets'}</Button></Card>
		</form>
	{/if}
</div>
