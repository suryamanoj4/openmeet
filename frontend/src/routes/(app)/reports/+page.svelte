<script lang="ts">
	import { onMount } from 'svelte';
	import { listEvents } from '$lib/services/events';
	import { listOrders } from '$lib/services/orders';
	import { listAttendees } from '$lib/services/attendees';
	import Card from '$lib/components/ui/card.svelte';
	import { BarChart3, Calendar, DollarSign, Users, Ticket } from 'lucide-svelte';
	import type { Event } from '$lib/graphql/types';

	let events = $state<Event[]>([]);
	let selectedEvent = $state<string>('');
	let orders = $state<{ id: string; total_amount: number; currency: string; status: string; payment_status: string }[]>([]);
	let attendees = $state<{ id: string; check_in_status: string }[]>([]);
	let loading = $state(false);

	onMount(async () => { events = await listEvents(); });

	async function loadStats() {
		if (!selectedEvent) return;
		loading = true;
		[orders, attendees] = await Promise.all([listOrders(selectedEvent), listAttendees(selectedEvent)]);
		loading = false;
	}

	$: totalRevenue = orders.filter(o => o.payment_status === 'paid').reduce((s, o) => s + Number(o.total_amount), 0);
	$: checkedIn = attendees.filter(a => a.check_in_status === 'checked_in').length;
	$: confirmedOrders = orders.filter(o => o.status === 'confirmed').length;
</script>

<div class="mx-auto max-w-7xl px-6 py-8">
	<div class="flex items-center justify-between mb-8">
		<div><h1 class="text-headline-xl font-bold text-fg"><BarChart3 size={28} class="inline mr-2 text-primary" />Reports</h1><p class="text-body-md text-on-surface-variant mt-1">Analytics and insights for your events</p></div>
	</div>

	<div class="mb-8">
		<select bind:value={selectedEvent} onchange={loadStats} class="h-10 rounded-lg border border-input bg-surface-container-lowest px-3 text-body-md min-w-[200px]">
			<option value="">Select an event</option>
			{#each events as e}<option value={e.id}>{e.name}</option>{/each}
		</select>
	</div>

	{#if !selectedEvent}
		<Card class="p-16 text-center"><BarChart3 size={40} class="mx-auto text-on-surface-variant/40 mb-4" /><h3 class="text-headline-md font-semibold text-fg">Select an event</h3><p class="text-body-md text-on-surface-variant mt-2">Choose an event to view its analytics</p></Card>
	{:else if loading}
		<div class="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">{#each [1,2,3,4] as _}<div class="h-32 rounded-xl bg-surface-container animate-pulse" />{/each}</div>
	{:else}
		<div class="grid gap-4 sm:grid-cols-2 lg:grid-cols-4 mb-8 animate-fade-in">
			<Card class="p-6"><div class="flex items-center gap-4"><div class="flex h-12 w-12 items-center justify-center rounded-xl bg-primary-fixed text-primary"><DollarSign size={24} /></div><div><p class="text-label-sm text-on-surface-variant">Revenue</p><p class="text-headline-lg font-bold text-fg">${totalRevenue.toFixed(2)}</p></div></div></Card>
			<Card class="p-6"><div class="flex items-center gap-4"><div class="flex h-12 w-12 items-center justify-center rounded-xl bg-secondary-fixed text-secondary"><Ticket size={24} /></div><div><p class="text-label-sm text-on-surface-variant">Orders</p><p class="text-headline-lg font-bold text-fg">{confirmedOrders}</p></div></div></Card>
			<Card class="p-6"><div class="flex items-center gap-4"><div class="flex h-12 w-12 items-center justify-center rounded-xl bg-tertiary-fixed text-tertiary"><Users size={24} /></div><div><p class="text-label-sm text-on-surface-variant">Attendees</p><p class="text-headline-lg font-bold text-fg">{attendees.length}</p></div></div></Card>
			<Card class="p-6"><div class="flex items-center gap-4"><div class="flex h-12 w-12 items-center justify-center rounded-xl bg-surface-container-high text-fg"><Calendar size={24} /></div><div><p class="text-label-sm text-on-surface-variant">Checked In</p><p class="text-headline-lg font-bold text-fg">{checkedIn}</p></div></div></Card>
		</div>

		<Card class="overflow-hidden">
			<div class="p-6 border-b border-outline-variant/60"><h2 class="text-headline-md font-semibold text-fg">Orders</h2></div>
			<div class="overflow-x-auto">
				<table class="w-full">
					<thead><tr class="border-b border-outline-variant/60 bg-surface-container-low">
						<th class="text-left px-4 py-3 text-label-sm text-on-surface-variant">ID</th>
						<th class="text-left px-4 py-3 text-label-sm text-on-surface-variant">Status</th>
						<th class="text-right px-4 py-3 text-label-sm text-on-surface-variant">Amount</th>
						<th class="text-right px-4 py-3 text-label-sm text-on-surface-variant">Payment</th>
					</tr></thead>
					<tbody>
						{#each orders as o}
							<tr class="border-b border-outline-variant/30">
								<td class="px-4 py-3 text-body-md text-fg font-mono text-sm">{o.id.slice(0,8)}</td>
								<td class="px-4 py-3"><span class="rounded-md px-2 py-0.5 text-label-sm {o.status === 'confirmed' ? 'bg-primary-fixed text-on-primary-fixed' : 'bg-surface-container-high text-on-surface-variant'}">{o.status}</span></td>
								<td class="px-4 py-3 text-body-md text-fg text-right font-medium">{o.currency === 'INR' ? '₹' : '$'}{Number(o.total_amount).toFixed(2)}</td>
								<td class="px-4 py-3 text-right"><span class="rounded-md px-2 py-0.5 text-label-sm {o.payment_status === 'paid' ? 'bg-primary-fixed text-on-primary-fixed' : 'bg-surface-container-high text-on-surface-variant'}">{o.payment_status}</span></td>
							</tr>
						{/each}
					</tbody>
				</table>
			</div>
		</Card>
	{/if}
</div>
