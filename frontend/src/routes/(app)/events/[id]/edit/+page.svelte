<script lang="ts">
	import { onMount } from 'svelte';
	import { goto } from '$app/navigation';
	import { page } from '$app/stores';
	import { getEvent, updateEvent } from '$lib/services/events';
	import { minimumFutureDatetime, toDatetimeLocalValue, toUpdateEventInput, validateEventSchedule, validateRegistrationWindow } from '$lib/services/event-input';
	import Button from '$lib/components/ui/button.svelte';
	import Input from '$lib/components/ui/input.svelte';
	import Label from '$lib/components/ui/label.svelte';
	import Card from '$lib/components/ui/card.svelte';
	import CardHeader from '$lib/components/ui/card-header.svelte';
	import CardTitle from '$lib/components/ui/card-title.svelte';
	import CardContent from '$lib/components/ui/card-content.svelte';
	import { ArrowLeft } from 'lucide-svelte';

	let name = $state(''); let slug = $state(''); let description = $state('');
	let event_type = $state('conference'); let venue_city = $state(''); let is_online = $state(false);
	let start_date = $state(''); let end_date = $state('');
	let timezone = $state('UTC'); let registration_start = $state(''); let registration_end = $state('');
	let venue_name = $state(''); let venue_address = $state(''); let venue_country = $state('');
	let online_url = $state(''); let max_attendees = $state<number | null>(null);
	let min_tickets_per_order = $state(1); let max_tickets_per_order = $state(10);
	let event_status = $state('draft'); let original_start_date = $state('');
	let cover_image_url = $state(''); let banner_image_url = $state('');
	let error = $state<string | null>(null); let saving = $state(false); let loading = $state(true);
	let eid = $state('');

	onMount(async () => {
		eid = $page.params.id as string;
		const event = await getEvent(eid);
		if (event) {
			name = event.name; slug = event.slug; description = event.description || '';
			event_type = event.event_type; venue_city = event.venue_city || '';
			timezone = event.timezone || 'UTC'; venue_name = event.venue_name || '';
			venue_address = typeof event.venue_address?.formatted === 'string' ? event.venue_address.formatted : '';
			venue_country = event.venue_country || ''; online_url = event.online_url || '';
			max_attendees = event.max_attendees ?? null;
			min_tickets_per_order = event.min_tickets_per_order;
			max_tickets_per_order = event.max_tickets_per_order;
			registration_start = event.registration_start ? toDatetimeLocalValue(event.registration_start) : '';
			registration_end = event.registration_end ? toDatetimeLocalValue(event.registration_end) : '';
			start_date = toDatetimeLocalValue(event.start_date); end_date = toDatetimeLocalValue(event.end_date);
			original_start_date = start_date; event_status = event.status;
			is_online = event.is_online; cover_image_url = event.cover_image_url || '';
			banner_image_url = event.banner_image_url || '';
		}
		loading = false;
	});

	async function handleSubmit(e: Event) {
		e.preventDefault(); error = null; saving = true;
		try {
			const allowPastStart = event_status === 'published' && start_date === original_start_date;
			const scheduleError = validateEventSchedule(start_date, end_date, new Date(), allowPastStart);
			if (scheduleError) {
				error = scheduleError;
				return;
			}
			const registrationError = validateRegistrationWindow(
				registration_start,
				registration_end,
				start_date,
				end_date,
				new Date(),
				event_status !== 'published'
			);
			if (registrationError) {
				error = registrationError;
				return;
			}
			await updateEvent(eid, toUpdateEventInput({
				name, slug, description, event_type, start_date, end_date,
				timezone, registration_start, registration_end,
				venue_name, venue_address, venue_city, venue_country,
				is_online, online_url, max_attendees, min_tickets_per_order,
				max_tickets_per_order, cover_image_url, banner_image_url
			}));
			goto(`/events/${eid}`);
		} catch (err) { error = err instanceof Error ? err.message : 'Failed'; } finally { saving = false; }
	}

	let minimumStart = $derived(minimumFutureDatetime());
</script>

<div class="mx-auto max-w-2xl px-6 py-8">
	<button onclick={() => goto(`/events/${eid}`)} class="flex items-center gap-2 text-body-md text-on-surface-variant hover:text-fg mb-6 transition-colors"><ArrowLeft size={18} /> Back</button>
	<Card>
		<CardHeader><CardTitle>Edit Event</CardTitle></CardHeader>
		<CardContent>
			{#if loading}<div class="h-48 animate-pulse rounded-lg bg-surface-container"></div>
			{:else}
				<form onsubmit={handleSubmit} class="space-y-5">
					{#if error}<div class="rounded-lg border border-error-container/50 bg-error-container/10 p-3"><p class="text-body-md text-error">{error}</p></div>{/if}
					<div class="space-y-1.5"><Label for="name">Name</Label><Input id="name" bind:value={name} required /></div>
					<div class="space-y-1.5">
						<Label for="slug">Slug</Label>
						<Input id="slug" bind:value={slug} disabled />
						<p class="text-label-sm text-on-surface-variant">The event slug cannot be changed.</p>
					</div>
					<div class="space-y-1.5"><Label for="desc">Description</Label><textarea id="desc" bind:value={description} class="flex min-h-[80px] w-full rounded-lg border border-input bg-surface-container-lowest px-3 py-2 text-body-md focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"></textarea></div>
					<div class="space-y-1.5"><Label for="type">Type</Label><select id="type" bind:value={event_type} class="flex h-10 w-full rounded-lg border border-input bg-surface-container-lowest px-3 text-body-md"><option value="conference">Conference</option><option value="workshop">Workshop</option><option value="meetup">Meetup</option><option value="webinar">Webinar</option><option value="hackathon">Hackathon</option></select></div>
					<div class="grid grid-cols-2 gap-4">
						<div class="space-y-1.5"><Label for="sd">Start Date</Label><Input id="sd" type="datetime-local" min={minimumStart} bind:value={start_date} required /></div>
						<div class="space-y-1.5"><Label for="ed">End Date</Label><Input id="ed" type="datetime-local" min={start_date || minimumStart} bind:value={end_date} required /></div>
					</div>
					<div class="space-y-1.5"><Label for="timezone">Timezone</Label><Input id="timezone" bind:value={timezone} required /></div>
					<div class="grid grid-cols-2 gap-4">
						<div class="space-y-1.5"><Label for="registration-start">Registration Opens</Label><Input id="registration-start" type="datetime-local" max={start_date || undefined} bind:value={registration_start} /></div>
						<div class="space-y-1.5"><Label for="registration-end">Registration Closes</Label><Input id="registration-end" type="datetime-local" min={registration_start || undefined} max={end_date || undefined} bind:value={registration_end} /></div>
					</div>
					<div class="grid grid-cols-2 gap-4">
						<div class="space-y-1.5"><Label for="venue-name">Venue Name</Label><Input id="venue-name" bind:value={venue_name} /></div>
						<div class="space-y-1.5"><Label for="country">Country</Label><Input id="country" bind:value={venue_country} /></div>
					</div>
					<div class="space-y-1.5"><Label for="address">Venue Address</Label><Input id="address" bind:value={venue_address} /></div>
					<div class="grid grid-cols-2 gap-4">
						<div class="space-y-1.5"><Label for="city">City</Label><Input id="city" bind:value={venue_city} /></div>
						<div class="space-y-1.5 flex items-end pb-2"><label class="flex items-center gap-2 cursor-pointer"><input type="checkbox" bind:checked={is_online} class="w-4 h-4 rounded border-outline-variant text-primary" /><span class="text-body-md text-fg">Online event</span></label></div>
					</div>
					{#if is_online}<div class="space-y-1.5"><Label for="online-url">Online Event URL</Label><Input id="online-url" type="url" bind:value={online_url} /></div>{/if}
					<div class="grid grid-cols-3 gap-4">
						<div class="space-y-1.5"><Label for="capacity">Capacity</Label><Input id="capacity" type="number" min="1" step="1" bind:value={max_attendees} /></div>
						<div class="space-y-1.5"><Label for="minimum-tickets">Minimum / order</Label><Input id="minimum-tickets" type="number" min="1" step="1" bind:value={min_tickets_per_order} /></div>
						<div class="space-y-1.5"><Label for="maximum-tickets">Maximum / order</Label><Input id="maximum-tickets" type="number" min={min_tickets_per_order} step="1" bind:value={max_tickets_per_order} /></div>
					</div>
					<div class="grid grid-cols-2 gap-4">
						<div class="space-y-1.5"><Label for="cover">Cover Image URL</Label><Input id="cover" type="url" bind:value={cover_image_url} /></div>
						<div class="space-y-1.5"><Label for="banner">Banner Image URL</Label><Input id="banner" type="url" bind:value={banner_image_url} /></div>
					</div>
					<div class="flex gap-3 pt-2"><Button type="submit" variant="primary" size="lg" isLoading={saving}>Save</Button><Button type="button" variant="outline" size="lg" onclick={() => goto(`/events/${eid}`)}>Cancel</Button></div>
				</form>
			{/if}
		</CardContent>
	</Card>
</div>
