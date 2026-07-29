<script lang="ts">
	import { goto } from '$app/navigation';
	import { page } from '$app/state';
	import { ambientAuth } from '$lib/ambient-auth.svelte';
	import Button from '$lib/components/ui/button.svelte';
	import EventCard from '$lib/components/event-card.svelte';
	import {
		buildDiscoveryUrl,
		clearDiscoveryUrl,
		filterEvents,
		getCategories,
		getVenues,
		groupEventsByDay
	} from '$lib/discovery';
	import type { DiscoveryView } from '$lib/discovery';
	import {
		Search,
		MapPin,
		Calendar,
		ChevronLeft,
		ChevronRight,
		Tags,
		Building2,
		X
	} from 'lucide-svelte';
	import type { HomePageData } from './+page';

	let { data }: { data: HomePageData } = $props();

	let featuredEl = $state<HTMLDivElement>();
	let heroSearch = $state('');
	let heroVenue = $state('');
	let heroDate = $state('');

	let view = $derived((page.url.searchParams.get('view') ?? 'explore') as DiscoveryView);
	let query = $derived(page.url.searchParams.get('q') ?? '');
	let category = $derived(page.url.searchParams.get('category') ?? '');
	let dateFilter = $derived(page.url.searchParams.get('date') ?? '');
	let venue = $derived(page.url.searchParams.get('venue') ?? '');
	let sort = $derived(page.url.searchParams.get('sort') ?? (view === 'calendar' ? 'date' : 'relevant'));

	let categories = $derived(getCategories(data.events));
	let venues = $derived(getVenues(data.events));
	let filteredEvents = $derived(
		filterEvents(data.events, {
			q: query,
			category,
			date: dateFilter,
			venue,
			sort
		})
	);
	let calendarGroups = $derived(groupEventsByDay(filteredEvents));
	let hasFilters = $derived(Boolean(query || category || dateFilter || venue || sort !== 'relevant'));

	$effect(() => {
		heroSearch = query;
		heroVenue = venue;
		heroDate = dateFilter;
	});

	function humanize(value: string): string {
		return value
			.replace(/[-_]/g, ' ')
			.replace(/\b\w/g, (letter) => letter.toUpperCase());
	}

	function formatDay(date: Date): string {
		return date.toLocaleDateString('en-US', {
			weekday: 'long',
			month: 'long',
			day: 'numeric',
			year: 'numeric'
		});
	}

	function handleRegister(eventId: string) {
		goto(`/event/${eventId}/checkout`);
	}

	function handleCreateEvent() {
		if (ambientAuth.isAuthenticated) {
			goto('/events/new');
		} else {
			ambientAuth.requireAuth({
				kind: 'create-event',
				label: 'Create an event',
				execute: () => goto('/events/new')
			});
		}
	}

	function updateDiscovery(
		changes: Record<string, string | null>,
		nextView: DiscoveryView = view
	) {
		goto(buildDiscoveryUrl(page.url.searchParams, changes, nextView), {
			keepFocus: true,
			noScroll: false
		});
	}

	function clearFilters() {
		goto(clearDiscoveryUrl(view));
	}

	function handleHeroSearch(event: SubmitEvent) {
		event.preventDefault();
		updateDiscovery(
			{
				q: heroSearch.trim() || null,
				venue: heroVenue.trim() || null,
				date: heroDate || null,
				category: null
			},
			'explore'
		);
	}

	function scrollFeatured(direction: number) {
		featuredEl?.scrollBy({ left: direction * 480, behavior: 'smooth' });
	}

	const dateOptions = [
		{ value: 'today', label: 'Today' },
		{ value: 'tomorrow', label: 'Tomorrow' },
		{ value: 'week', label: 'This Week' },
		{ value: 'month', label: 'Next Month' }
	];
</script>

<section class="relative h-[520px] md:h-[600px] flex items-center justify-center overflow-hidden bg-gradient-to-br from-on-surface via-inverse-surface to-on-surface">
	<div class="absolute inset-0 bg-gradient-to-r from-on-surface/90 via-on-surface/50 to-transparent"></div>
	<div class="absolute -right-32 -top-32 h-96 w-96 rounded-full bg-primary-container/20 blur-3xl"></div>
	<div class="absolute -left-32 -bottom-32 h-80 w-80 rounded-full bg-tertiary-container/10 blur-3xl"></div>

	<div class="relative z-10 max-w-[1440px] mx-auto px-6 w-full">
		<div class="max-w-2xl">
			<span class="inline-flex items-center rounded-full bg-primary-fixed-dim/20 backdrop-blur px-4 py-1.5 text-label-sm text-inverse-on-surface border border-white/10">
				Professional Event Management
			</span>
			<h1 class="font-headline-xl text-headline-xl text-white mt-6 mb-4 leading-tight sm:text-5xl">
				Discover Your Next Experience
			</h1>
			<p class="text-body-lg font-body-lg text-white/80 mb-8 max-w-lg">
				From high-tech summits to intimate jazz nights, find the events that shape your professional and social world.
			</p>

			<form class="glass-card p-2 rounded-2xl flex flex-col md:flex-row gap-2 shadow-glass border border-white/20" onsubmit={handleHeroSearch}>
				<div class="flex-1 relative md:border-r border-white/10 px-4 py-3">
					<label for="search-what" class="block text-[10px] uppercase font-bold text-on-surface-variant mb-1 tracking-wider">What</label>
					<div class="flex items-center gap-2">
						<Search size={18} class="text-primary shrink-0" />
						<input id="search-what" type="search" placeholder="Event name or keyword" bind:value={heroSearch} class="bg-transparent border-none p-0 focus:ring-0 text-fg font-medium placeholder:text-on-surface-variant/50 w-full outline-none" />
					</div>
				</div>
				<div class="flex-1 relative md:border-r border-white/10 px-4 py-3">
					<label for="search-where" class="block text-[10px] uppercase font-bold text-on-surface-variant mb-1 tracking-wider">Where</label>
					<div class="flex items-center gap-2">
						<MapPin size={18} class="text-primary shrink-0" />
						<input id="search-where" type="search" placeholder="City or online" bind:value={heroVenue} class="bg-transparent border-none p-0 focus:ring-0 text-fg font-medium placeholder:text-on-surface-variant/50 w-full outline-none" />
					</div>
				</div>
				<div class="flex-1 relative px-4 py-3">
					<label for="search-when" class="block text-[10px] uppercase font-bold text-on-surface-variant mb-1 tracking-wider">When</label>
					<div class="flex items-center gap-2">
						<Calendar size={18} class="text-primary shrink-0" />
						<select id="search-when" bind:value={heroDate} class="bg-transparent border-none p-0 focus:ring-0 text-fg font-medium w-full outline-none">
							<option value="">Any date</option>
							{#each dateOptions as option}
								<option value={option.value}>{option.label}</option>
							{/each}
						</select>
					</div>
				</div>
				<button type="submit" class="bg-primary text-on-primary px-8 py-4 rounded-xl font-bold hover:bg-primary-container transition-all flex items-center justify-center gap-2 shadow-sm shrink-0">
					<Search size={18} />
					<span>Search</span>
				</button>
			</form>
		</div>
	</div>
</section>

<section class="py-16 max-w-[1440px] mx-auto px-6">
	<div class="flex items-end justify-between mb-8">
		<div>
			<h2 class="text-headline-lg font-semibold text-fg">Featured Events</h2>
			<p class="text-body-md text-on-surface-variant mt-1">Hand-picked experiences you can't miss this month.</p>
		</div>
		<div class="hidden sm:flex gap-2">
			<button aria-label="Previous featured events" onclick={() => scrollFeatured(-1)} class="p-2 rounded-full border border-outline-variant hover:bg-surface-container-low transition-colors text-on-surface-variant hover:text-fg">
				<ChevronLeft size={20} />
			</button>
			<button aria-label="Next featured events" onclick={() => scrollFeatured(1)} class="p-2 rounded-full border border-outline-variant hover:bg-surface-container-low transition-colors text-on-surface-variant hover:text-fg">
				<ChevronRight size={20} />
			</button>
		</div>
	</div>

	{#if data.events.length > 0}
		<div bind:this={featuredEl} class="flex gap-6 overflow-x-auto pb-6 scrollbar-hide">
			{#each data.events.slice(0, 6) as event}
				<div class="min-w-[340px] md:min-w-[450px] group relative overflow-hidden rounded-xl h-[280px] md:h-[300px] shadow-lg flex-shrink-0 bg-surface-container">
					{#if event.cover_image_url}
						<img src={event.cover_image_url} alt={event.name} class="w-full h-full object-cover transition-transform duration-500 group-hover:scale-110" />
					{:else}
						<div class="w-full h-full bg-gradient-to-br from-primary-fixed-dim/30 to-surface-container-highest flex items-center justify-center"><Calendar size={32} class="text-primary" /></div>
					{/if}
					<div class="absolute inset-0 bg-gradient-to-t from-black/90 via-black/30 to-transparent"></div>
					<div class="absolute bottom-0 left-0 p-6 w-full">
						<span class="bg-primary text-on-primary text-[10px] font-bold uppercase px-2.5 py-1 rounded-sm mb-3 inline-block tracking-wider">{event.event_type || 'Event'}</span>
						<h3 class="text-white text-headline-md font-semibold mb-2">{event.name}</h3>
						<div class="flex items-center justify-between gap-3">
							<p class="text-white/80 text-body-md">
								{new Date(event.start_date).toLocaleDateString('en-US', { month: 'short', day: 'numeric' })}
								{event.venue_city ? `• ${event.venue_city}` : event.is_online ? '• Online' : ''}
							</p>
							<button onclick={() => handleRegister(event.id)} class="bg-white text-primary px-4 py-2 rounded-lg font-bold text-sm hover:bg-primary-fixed transition-colors">View Event</button>
						</div>
					</div>
				</div>
			{/each}
		</div>
	{:else}
		<div class="rounded-xl border border-outline-variant bg-surface-container-low p-12 text-center text-on-surface-variant">Featured events are coming soon.</div>
	{/if}
</section>

<section id="discover" class="bg-surface-container-low py-16 scroll-mt-16">
	<div class="max-w-[1440px] mx-auto px-6">
		<div class="flex flex-col gap-4 sm:flex-row sm:items-end sm:justify-between mb-8">
			<div>
				<p class="text-label-sm uppercase tracking-wider font-bold text-primary mb-2">{humanize(view)}</p>
				<h2 class="text-headline-lg font-semibold text-fg">
					{view === 'calendar' ? 'Events Calendar' : view === 'venues' ? 'Browse by Venue' : view === 'categories' ? 'Browse by Category' : 'Discover Events'}
				</h2>
				<p class="text-body-md text-on-surface-variant mt-1">{filteredEvents.length} event{filteredEvents.length !== 1 ? 's' : ''} found</p>
			</div>
			<div class="flex items-center gap-3">
				{#if hasFilters}
					<button onclick={clearFilters} class="inline-flex items-center gap-1.5 text-label-md font-semibold text-primary hover:underline"><X size={15} /> Clear all</button>
				{/if}
				<label for="sort-events" class="sr-only">Sort events</label>
				<select id="sort-events" value={sort} onchange={(event) => updateDiscovery({ sort: event.currentTarget.value === 'relevant' ? null : event.currentTarget.value })} class="h-10 rounded-lg border border-outline-variant bg-surface-container-lowest px-3 text-label-md font-semibold text-primary outline-none focus:ring-2 focus:ring-primary">
					<option value="relevant">Relevant</option>
					<option value="date">Date (Soonest)</option>
					<option value="name">Name (A–Z)</option>
				</select>
			</div>
		</div>

		{#if view === 'categories'}
			<div class="grid gap-3 sm:grid-cols-2 lg:grid-cols-5 mb-8">
				{#each categories as item}
					<button onclick={() => updateDiscovery({ category: category === item ? null : item })} class="flex items-center gap-3 rounded-xl border p-4 text-left transition-all {category === item ? 'border-primary bg-primary text-on-primary shadow-md' : 'border-outline-variant bg-surface-container-lowest text-fg hover:border-primary'}">
						<Tags size={20} />
						<span class="font-semibold">{humanize(item)}</span>
					</button>
				{/each}
			</div>
		{:else if view === 'calendar'}
			<div class="flex flex-wrap gap-2 mb-8">
				{#each dateOptions as option}
					<button onclick={() => updateDiscovery({ date: dateFilter === option.value ? null : option.value, sort: 'date' })} class="px-4 py-2 rounded-lg border text-label-md font-semibold transition-all {dateFilter === option.value ? 'bg-primary border-primary text-on-primary' : 'bg-surface-container-lowest border-outline-variant text-on-surface-variant hover:border-primary hover:text-primary'}">{option.label}</button>
				{/each}
			</div>
		{:else if view === 'venues'}
			<div class="grid gap-3 sm:grid-cols-2 lg:grid-cols-4 mb-8">
				{#each venues as item}
					<button onclick={() => updateDiscovery({ venue: venue === item ? null : item })} class="flex items-center gap-3 rounded-xl border p-4 text-left transition-all {venue === item ? 'border-primary bg-primary text-on-primary shadow-md' : 'border-outline-variant bg-surface-container-lowest text-fg hover:border-primary'}">
						<Building2 size={20} />
						<span class="font-semibold">{item}</span>
					</button>
				{/each}
			</div>
		{/if}

		<div class="flex flex-col lg:flex-row gap-8">
			{#if view === 'explore'}
				<aside class="w-full lg:w-64 shrink-0">
					<div class="sticky top-24 space-y-7 rounded-xl border border-outline-variant bg-surface-container-lowest p-5">
						<div>
							<h3 class="text-label-md font-semibold text-fg mb-3">Category</h3>
							<div class="space-y-2">
								{#each categories as item}
									<button onclick={() => updateDiscovery({ category: category === item ? null : item })} class="block w-full rounded-lg px-3 py-2 text-left text-body-md transition-colors {category === item ? 'bg-primary-fixed text-primary font-semibold' : 'text-on-surface-variant hover:bg-surface-container-low'}">{humanize(item)}</button>
								{/each}
							</div>
						</div>
						<div>
							<h3 class="text-label-md font-semibold text-fg mb-3">Date</h3>
							<div class="grid grid-cols-2 gap-2">
								{#each dateOptions as option}
									<button onclick={() => updateDiscovery({ date: dateFilter === option.value ? null : option.value })} class="px-2 py-2 rounded-lg border text-label-sm font-semibold {dateFilter === option.value ? 'bg-primary border-primary text-on-primary' : 'border-outline-variant text-on-surface-variant hover:border-primary'}">{option.label}</button>
								{/each}
							</div>
						</div>
						<div>
							<label for="venue-filter" class="text-label-md font-semibold text-fg mb-3 block">Venue</label>
							<select id="venue-filter" value={venue} onchange={(event) => updateDiscovery({ venue: event.currentTarget.value || null })} class="w-full h-10 rounded-lg border border-outline-variant bg-surface-container-low px-3 text-body-md outline-none focus:ring-2 focus:ring-primary">
								<option value="">All venues</option>
								{#each venues as item}<option value={item}>{item}</option>{/each}
							</select>
						</div>
					</div>
				</aside>
			{/if}

			<div class="flex-1 min-w-0">
				{#if data.error}
					<div class="rounded-xl border border-error-container/50 bg-error-container/10 p-6 text-error">{data.error}</div>
				{:else if filteredEvents.length === 0}
					<div class="rounded-xl border border-outline-variant bg-surface-container-lowest p-14 text-center">
						<Calendar size={40} class="mx-auto text-on-surface-variant/40 mb-4" />
						<h3 class="text-headline-md font-semibold text-fg">No matching events</h3>
						<p class="text-body-md text-on-surface-variant mt-2">Try clearing a filter or searching for something else.</p>
						<div class="flex justify-center gap-3 mt-6">
							<Button variant="outline" size="lg" onclick={clearFilters}>Clear filters</Button>
							<Button variant="primary" size="lg" onclick={handleCreateEvent}>Create an event</Button>
						</div>
					</div>
				{:else if view === 'calendar'}
					<div class="space-y-10">
						{#each calendarGroups as group}
							<section>
								<div class="flex items-center gap-3 mb-4">
									<div class="flex h-10 w-10 items-center justify-center rounded-lg bg-primary-fixed text-primary"><Calendar size={19} /></div>
									<h3 class="text-headline-md font-semibold text-fg">{formatDay(group.date)}</h3>
								</div>
								<div class="grid gap-5 md:grid-cols-2 xl:grid-cols-3">
									{#each group.events as event}<EventCard {event} onRegister={handleRegister} />{/each}
								</div>
							</section>
						{/each}
					</div>
				{:else}
					<div class="grid gap-6 md:grid-cols-2 xl:grid-cols-3">
						{#each filteredEvents as event}<EventCard {event} onRegister={handleRegister} />{/each}
					</div>
				{/if}
			</div>
		</div>
	</div>
</section>

<footer class="bg-surface-container-lowest border-t border-outline-variant/60">
	<div class="flex flex-col md:flex-row justify-between items-center py-12 px-6 max-w-[1440px] mx-auto gap-6">
		<div class="flex flex-col items-center md:items-start gap-3">
			<a href="/" class="flex items-center gap-2">
				<div class="flex h-7 w-7 items-center justify-center rounded-md bg-primary text-on-primary text-xs font-bold">O</div>
				<span class="text-headline-md font-bold text-fg">OpenMeet</span>
			</a>
			<p class="text-body-md text-on-surface-variant max-w-xs text-center md:text-left">The leading platform for discovering and managing premium events globally.</p>
		</div>
		<p class="text-body-md text-on-surface-variant">&copy; {new Date().getFullYear()} OpenMeet. All rights reserved.</p>
	</div>
</footer>
