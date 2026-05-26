<script lang="ts">
	import { onMount } from 'svelte';
	import { page } from '$app/stores';
	import { listAttendees, checkIn, undoCheckIn } from '$lib/services/attendees';
	import { listEvents } from '$lib/services/events';
	import Button from '$lib/components/ui/button.svelte';
	import Card from '$lib/components/ui/card.svelte';
	import { Users, Search, Check, X } from 'lucide-svelte';
	import { currentUser } from '$lib/stores/auth';
	import type { Event } from '$lib/graphql/types';

	let attendees = $state<{ id: string; first_name: string; last_name: string; email: string; check_in_status: string; check_in_at?: string; ticket_id?: string }[]>([]);
	let events = $state<Event[]>([]);
	let selectedEvent = $state<string | undefined>($page.url.searchParams.get('eventId') || undefined);
	let searchQuery = $state('');
	let loading = $state(true);

	onMount(async () => { events = await listEvents(); await loadAttendees(); });

	async function loadAttendees() {
		loading = true;
		attendees = selectedEvent ? await listAttendees(selectedEvent) : [];
		loading = false;
	}

	let filtered = $derived(searchQuery
		? attendees.filter(a =>
			a.first_name.toLowerCase().includes(searchQuery.toLowerCase()) ||
			a.last_name.toLowerCase().includes(searchQuery.toLowerCase()) ||
			a.email.toLowerCase().includes(searchQuery.toLowerCase()))
		: attendees
	);

	async function handleCheckIn(id: string) {
		const user = $currentUser;
		if (!user) return;
		const result = await checkIn(id, user.id);
		if (result) await loadAttendees();
	}

	async function handleUndo(id: string) {
		await undoCheckIn(id);
		await loadAttendees();
	}
</script>

<div class="mx-auto max-w-7xl px-6 py-8">
	<div class="flex items-center justify-between mb-8">
		<div><h1 class="text-headline-xl font-bold text-fg">Attendees</h1><p class="text-body-md text-on-surface-variant mt-1">Manage event attendees and check-ins</p></div>
	</div>

	<div class="flex flex-wrap gap-3 mb-6">
		<select bind:value={selectedEvent} onchange={loadAttendees} class="h-10 rounded-lg border border-input bg-surface-container-lowest px-3 text-body-md">
			<option value={undefined}>Select an event</option>
			{#each events as e}<option value={e.id}>{e.name}</option>{/each}
		</select>
		<div class="relative flex-1 max-w-xs">
			<Search size={16} class="absolute left-3 top-1/2 -translate-y-1/2 text-on-surface-variant" />
			<input type="text" placeholder="Search attendees..." bind:value={searchQuery} class="w-full h-10 pl-9 pr-4 rounded-lg border border-input bg-surface-container-lowest text-body-md focus:ring-2 focus:ring-primary outline-none" />
		</div>
		<span class="text-body-md text-on-surface-variant self-center">{filtered.length} attendees</span>
	</div>

	{#if !selectedEvent}
		<Card class="p-16 text-center"><Users size={40} class="mx-auto text-on-surface-variant/40 mb-4" /><h3 class="text-headline-md font-semibold text-fg">Select an event</h3><p class="text-body-md text-on-surface-variant mt-2">Choose an event to view its attendees</p></Card>
	{:else if loading}
		<div class="space-y-3">{#each [1,2,3] as _}<div class="h-16 rounded-xl bg-surface-container animate-pulse"></div>{/each}</div>
	{:else if filtered.length === 0}
		<Card class="p-16 text-center"><Users size={40} class="mx-auto text-on-surface-variant/40 mb-4" /><h3 class="text-headline-md text-fg">No attendees</h3></Card>
	{:else}
		<Card class="overflow-hidden">
			<div class="overflow-x-auto">
				<table class="w-full">
					<thead><tr class="border-b border-outline-variant/60 bg-surface-container-low">
						<th class="text-left px-4 py-3 text-label-sm text-on-surface-variant">Name</th>
						<th class="text-left px-4 py-3 text-label-sm text-on-surface-variant">Email</th>
						<th class="text-left px-4 py-3 text-label-sm text-on-surface-variant">Status</th>
						<th class="text-right px-4 py-3 text-label-sm text-on-surface-variant">Action</th>
					</tr></thead>
					<tbody>
						{#each filtered as a}
							<tr class="border-b border-outline-variant/30 hover:bg-surface-container-low/50 transition-colors">
								<td class="px-4 py-3 text-body-md text-fg">{a.first_name} {a.last_name}</td>
								<td class="px-4 py-3 text-body-md text-on-surface-variant">{a.email}</td>
								<td class="px-4 py-3">
									{#if a.check_in_status === 'checked_in'}
										<span class="inline-flex items-center gap-1 rounded-md bg-primary-fixed px-2 py-0.5 text-label-sm text-on-primary-fixed">Checked in</span>
									{:else}
										<span class="inline-flex items-center gap-1 rounded-md bg-surface-container-high px-2 py-0.5 text-label-sm text-on-surface-variant">Not checked in</span>
									{/if}
								</td>
								<td class="px-4 py-3 text-right">
									{#if a.check_in_status === 'checked_in'}
										<Button variant="ghost" size="sm" onclick={() => handleUndo(a.id)}><X size={14} class="mr-1" />Undo</Button>
									{:else}
										<Button variant="primary" size="sm" onclick={() => handleCheckIn(a.id)}><Check size={14} class="mr-1" />Check In</Button>
									{/if}
								</td>
							</tr>
						{/each}
					</tbody>
				</table>
			</div>
		</Card>
	{/if}
</div>
