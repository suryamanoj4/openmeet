<script lang="ts">
	import { onMount } from 'svelte';
	import { listEvents } from '$lib/services/events';
	import { searchAttendees, checkIn } from '$lib/services/attendees';
	import Button from '$lib/components/ui/button.svelte';
	import Card from '$lib/components/ui/card.svelte';
	import { QrCode, Search, Check, UserCheck } from 'lucide-svelte';
	import { currentUser } from '$lib/stores/auth';
	import type { Event } from '$lib/graphql/types';

	let events = $state<Event[]>([]);
	let selectedEvent = $state<string>('');
	let query = $state('');
	let results = $state<{ id: string; first_name: string; last_name: string; email: string; check_in_status: string }[]>([]);
	let message = $state<{ text: string; type: 'success' | 'error' } | null>(null);
	let searching = $state(false);

	onMount(async () => { events = await listEvents(); });

	let debounce: ReturnType<typeof setTimeout>;
	async function handleSearch(val: string) {
		query = val; message = null;
		clearTimeout(debounce);
		if (!val || !selectedEvent) { results = []; return; }
		debounce = setTimeout(async () => {
			searching = true;
			results = await searchAttendees(selectedEvent, val);
			searching = false;
		}, 300);
	}

	async function handleCheckIn(attendeeId: string) {
		const user = $currentUser; if (!user) return;
		message = null;
		const result = await checkIn(attendeeId, user.id);
		if (result) {
			message = { text: 'Checked in successfully!', type: 'success' };
			results = results.map(r => r.id === attendeeId ? { ...r, check_in_status: 'checked_in' } : r);
		} else {
			message = { text: 'Check-in failed', type: 'error' };
		}
		setTimeout(() => message = null, 3000);
	}
</script>

<div class="mx-auto max-w-2xl px-6 py-8">
	<div class="text-center mb-8">
		<div class="mx-auto flex h-16 w-16 items-center justify-center rounded-2xl bg-primary-fixed"><QrCode size={32} class="text-primary" /></div>
		<h1 class="text-headline-xl font-bold text-fg mt-4">Check-In</h1>
		<p class="text-body-md text-on-surface-variant mt-1">Search for attendees to check them in</p>
	</div>

	<Card class="p-6 mb-6">
		<div class="space-y-4">
			<select bind:value={selectedEvent} onchange={() => { results = []; query = ''; }} class="h-10 w-full rounded-lg border border-input bg-surface-container-lowest px-3 text-body-md">
				<option value="">Select an event</option>
				{#each events as e}<option value={e.id}>{e.name}</option>{/each}
			</select>

			<div class="relative">
				<Search size={18} class="absolute left-3 top-1/2 -translate-y-1/2 text-on-surface-variant" />
				<input type="text" placeholder="Search by name or email..." bind:value={query} oninput={(e) => handleSearch(e.currentTarget.value)}
					class="w-full h-12 pl-10 pr-4 rounded-xl border border-input bg-surface-container-lowest text-body-md focus:ring-2 focus:ring-primary outline-none"
					disabled={!selectedEvent} />
			</div>
		</div>
	</Card>

	{#if message}
		<div class="rounded-xl p-4 mb-4 text-center animate-fade-in {message.type === 'success' ? 'bg-primary-fixed text-on-primary-fixed' : 'bg-error-container text-on-error-container'}">
			<p class="text-label-md">{message.text}</p>
		</div>
	{/if}

	{#if searching}
		<div class="space-y-3">{#each [1,2] as _}<div class="h-20 rounded-xl bg-surface-container animate-pulse"></div>{/each}</div>
	{:else if results.length > 0}
		<div class="space-y-3 animate-fade-in">
			{#each results as r}
				<Card class="p-4 flex items-center justify-between">
					<div>
						<p class="text-headline-md font-semibold text-fg">{r.first_name} {r.last_name}</p>
						<p class="text-body-md text-on-surface-variant">{r.email}</p>
						{#if r.check_in_status === 'checked_in'}
							<span class="inline-flex items-center gap-1 rounded-md bg-primary-fixed px-2 py-0.5 text-label-sm text-on-primary-fixed mt-1"><Check size={12} /> Checked in</span>
						{/if}
					</div>
					{#if r.check_in_status !== 'checked_in'}
						<Button variant="primary" onclick={() => handleCheckIn(r.id)}>
							<UserCheck size={16} class="mr-1" /> Check In
						</Button>
					{/if}
				</Card>
			{/each}
		</div>
	{:else if query && !searching}
		<Card class="p-8 text-center"><p class="text-body-md text-on-surface-variant">No attendees found matching "{query}"</p></Card>
	{/if}
</div>
