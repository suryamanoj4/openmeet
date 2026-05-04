<script lang="ts">
	import { goto } from '$app/navigation';
	import { ambientAuth } from '$lib/ambient-auth.svelte';
	import Button from '$lib/components/ui/button.svelte';
	import EventCard from '$lib/components/event-card.svelte';
	import { Search, MapPin, Calendar, ChevronLeft, ChevronRight } from 'lucide-svelte';
	import type { HomePageData } from './+page';

	let { data }: { data: HomePageData } = $props();

	let selectedCategories = $state<string[]>(['music']);
	let dateFilter = $state('week');
	let searchQuery = $state('');

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

	function toggleCategory(cat: string) {
		if (selectedCategories.includes(cat)) {
			selectedCategories = selectedCategories.filter(c => c !== cat);
		} else {
			selectedCategories = [...selectedCategories, cat];
		}
	}

	const categories = ['Technology', 'Music & Arts', 'Food & Drink', 'Business', 'Health & Wellness'];
</script>

<!-- Hero Section -->
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

			<div class="glass-card p-2 rounded-2xl flex flex-col md:flex-row gap-2 shadow-glass border border-white/20">
				<div class="flex-1 relative md:border-r border-white/10 px-4 py-3">
					<label for="search-what" class="block text-[10px] uppercase font-bold text-on-surface-variant mb-1 tracking-wider">What</label>
					<div class="flex items-center gap-2">
						<Search size={18} class="text-primary shrink-0" />
						<input
							id="search-what"
							type="text"
							placeholder="Event name or keyword"
							bind:value={searchQuery}
							class="bg-transparent border-none p-0 focus:ring-0 text-fg font-medium placeholder:text-on-surface-variant/50 w-full outline-none"
						/>
					</div>
				</div>
				<div class="flex-1 relative md:border-r border-white/10 px-4 py-3">
					<label for="search-where" class="block text-[10px] uppercase font-bold text-on-surface-variant mb-1 tracking-wider">Where</label>
					<div class="flex items-center gap-2">
						<MapPin size={18} class="text-primary shrink-0" />
						<input
							id="search-where"
							type="text"
							placeholder="San Francisco, CA"
							class="bg-transparent border-none p-0 focus:ring-0 text-fg font-medium placeholder:text-on-surface-variant/50 w-full outline-none"
						/>
					</div>
				</div>
				<div class="flex-1 relative px-4 py-3">
					<label for="search-when" class="block text-[10px] uppercase font-bold text-on-surface-variant mb-1 tracking-wider">When</label>
					<div class="flex items-center gap-2">
						<Calendar size={18} class="text-primary shrink-0" />
						<input
							id="search-when"
							type="text"
							placeholder="Any date"
							class="bg-transparent border-none p-0 focus:ring-0 text-fg font-medium placeholder:text-on-surface-variant/50 w-full outline-none"
						/>
					</div>
				</div>
				<button class="bg-primary text-on-primary px-8 py-4 rounded-xl font-bold hover:bg-primary-container transition-all flex items-center justify-center gap-2 shadow-sm shrink-0">
					<Search size={18} />
					<span>Search</span>
				</button>
			</div>
		</div>
	</div>
</section>

<!-- Featured Events -->
<section class="py-16 max-w-[1440px] mx-auto px-6">
	<div class="flex items-end justify-between mb-8">
		<div>
			<h2 class="text-headline-lg font-semibold text-fg">Featured Events</h2>
			<p class="text-body-md text-on-surface-variant mt-1">Hand-picked experiences you can't miss this month.</p>
		</div>
		<div class="hidden sm:flex gap-2">
			<button class="p-2 rounded-full border border-outline-variant hover:bg-surface-container-low transition-colors text-on-surface-variant hover:text-fg">
				<ChevronLeft size={20} />
			</button>
			<button class="p-2 rounded-full border border-outline-variant hover:bg-surface-container-low transition-colors text-on-surface-variant hover:text-fg">
				<ChevronRight size={20} />
			</button>
		</div>
	</div>

	{#if data.events.length > 0}
		<div class="flex gap-6 overflow-x-auto pb-6 scrollbar-hide">
			{#each data.events.slice(0, 3) as event}
				<div class="min-w-[380px] md:min-w-[450px] group relative overflow-hidden rounded-xl h-[280px] md:h-[300px] shadow-lg flex-shrink-0 bg-surface-container">
					{#if event.cover_image_url}
						<img src={event.cover_image_url} alt={event.name} class="w-full h-full object-cover transition-transform duration-500 group-hover:scale-110" />
					{:else}
						<div class="w-full h-full bg-gradient-to-br from-primary-fixed-dim/30 to-surface-container-highest flex items-center justify-center">
							<div class="flex h-16 w-16 items-center justify-center rounded-2xl bg-surface-container-lowest/80">
								<Calendar size={28} class="text-primary" />
							</div>
						</div>
					{/if}
					<div class="absolute inset-0 bg-gradient-to-t from-black/90 via-black/30 to-transparent"></div>
					<div class="absolute bottom-0 left-0 p-6 w-full">
						<span class="bg-primary text-on-primary text-[10px] font-bold uppercase px-2.5 py-1 rounded-sm mb-3 inline-block tracking-wider">
							{event.event_type || 'Event'}
						</span>
						<h3 class="text-white text-headline-md font-semibold mb-2">{event.name}</h3>
						<div class="flex items-center justify-between">
							<p class="text-white/80 text-body-md">
								{new Date(event.start_date).toLocaleDateString('en-US', { month: 'short', day: 'numeric' })}
								{event.venue_city ? `\u2022 ${event.venue_city}` : ''}
							</p>
							{#if ambientAuth.isAuthenticated}
								<button onclick={() => handleRegister(event.id)} class="bg-white text-primary px-4 py-2 rounded-lg font-bold text-sm hover:bg-primary-fixed transition-colors">
									Get Tickets
								</button>
							{:else}
								<button onclick={() => ambientAuth.requireAuth({ kind: 'register-ticket', label: 'Get tickets', execute: () => handleRegister(event.id) })} class="bg-white text-primary px-4 py-2 rounded-lg font-bold text-sm hover:bg-primary-fixed transition-colors">
									Get Tickets
								</button>
							{/if}
						</div>
					</div>
				</div>
			{/each}
		</div>
	{:else}
		<div class="flex gap-6 overflow-x-auto pb-6 scrollbar-hide">
			{#each [1, 2, 3] as _}
				<div class="min-w-[380px] md:min-w-[450px] rounded-xl h-[280px] md:h-[300px] bg-surface-container-higher overflow-hidden flex-shrink-0">
					<div class="w-full h-full bg-gradient-to-br from-surface-container-high to-surface-container flex items-center justify-center">
						<div class="text-center">
							<Calendar size={32} class="mx-auto text-on-surface-variant/40" />
							<p class="text-body-md text-on-surface-variant/40 mt-3">Featured event coming soon</p>
						</div>
					</div>
				</div>
			{/each}
		</div>
	{/if}
</section>

<!-- Discovery Grid -->
<section class="bg-surface-container-low py-16">
	<div class="max-w-[1440px] mx-auto px-6 flex flex-col lg:flex-row gap-8">
		<!-- Sidebar Filters -->
		<aside class="w-full lg:w-64 shrink-0">
			<div class="sticky top-24 space-y-8">
				<div class="flex items-center justify-between">
					<h4 class="text-headline-md font-semibold text-fg">Filters</h4>
					<button class="text-primary text-label-sm font-semibold hover:underline">Clear all</button>
				</div>

				<div>
					<h5 class="text-label-md text-fg mb-4">Category</h5>
					<div class="space-y-3">
						{#each categories as cat}
							<label class="flex items-center gap-3 cursor-pointer group">
								<input
									type="checkbox"
									checked={selectedCategories.includes(cat.toLowerCase())}
									onchange={() => toggleCategory(cat.toLowerCase())}
									class="w-4 h-4 rounded border-outline-variant text-primary focus:ring-primary transition-all"
								/>
								<span class="text-body-md text-on-surface-variant group-hover:text-primary transition-colors">{cat}</span>
							</label>
						{/each}
					</div>
				</div>

				<div>
					<h5 class="text-label-md text-fg mb-4">Date Range</h5>
					<div class="grid grid-cols-2 gap-2">
						<button
							class="px-3 py-2 border rounded-lg text-label-sm font-semibold transition-all {dateFilter === 'today' ? 'bg-surface-container-lowest border-primary text-primary' : 'border-outline-variant text-on-surface-variant hover:bg-surface-container-lowest hover:border-primary'}"
							onclick={() => dateFilter = 'today'}
						>Today</button>
						<button
							class="px-3 py-2 border rounded-lg text-label-sm font-semibold transition-all {dateFilter === 'tomorrow' ? 'bg-surface-container-lowest border-primary text-primary' : 'border-outline-variant text-on-surface-variant hover:bg-surface-container-lowest hover:border-primary'}"
							onclick={() => dateFilter = 'tomorrow'}
						>Tomorrow</button>
						<button
							class="px-3 py-2 border rounded-lg text-label-sm font-semibold transition-all {dateFilter === 'week' ? 'bg-surface-container-lowest border-primary text-primary' : 'border-outline-variant text-on-surface-variant hover:bg-surface-container-lowest hover:border-primary'}"
							onclick={() => dateFilter = 'week'}
						>This Week</button>
						<button
							class="px-3 py-2 border rounded-lg text-label-sm font-semibold transition-all {dateFilter === 'month' ? 'bg-surface-container-lowest border-primary text-primary' : 'border-outline-variant text-on-surface-variant hover:bg-surface-container-lowest hover:border-primary'}"
							onclick={() => dateFilter = 'month'}
						>Next Month</button>
					</div>
				</div>

				<div>
					<h5 class="text-label-md text-fg mb-4">Price Range</h5>
					<input
						type="range"
						min="0"
						max="1000"
						step="50"
						class="w-full h-2 bg-secondary-container rounded-lg appearance-none cursor-pointer accent-primary"
					/>
					<div class="flex justify-between mt-2 text-label-sm text-on-surface-variant font-medium">
						<span>Free</span>
						<span>$1000+</span>
					</div>
				</div>
			</div>
		</aside>

		<!-- Grid -->
		<div class="flex-1">
			<div class="flex items-center justify-between mb-6">
				<div>
					<h2 class="text-headline-lg font-semibold text-fg">Discover Events</h2>
					<p class="text-body-md text-on-surface-variant mt-1">
						{data.events.length} event{data.events.length !== 1 ? 's' : ''} found
					</p>
				</div>
				<div class="flex items-center gap-2">
					<span class="text-body-md text-on-surface-variant font-medium hidden sm:inline">Sort by:</span>
					<select class="bg-transparent border-none text-label-sm font-semibold text-primary focus:ring-0 cursor-pointer outline-none">
						<option>Relevant</option>
						<option>Date (Soonest)</option>
						<option>Price (Low to High)</option>
					</select>
				</div>
			</div>

			{#if data.error}
				<div class="rounded-xl border border-error-container/50 bg-error-container/10 p-12 text-center">
					<div class="mx-auto flex h-12 w-12 items-center justify-center rounded-full bg-error-container mb-4">
						<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="text-error"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/></svg>
					</div>
					<h3 class="text-headline-md text-error font-semibold">Failed to load events</h3>
					<p class="text-body-md text-on-surface-variant mt-2">{data.error}</p>
				</div>
			{:else if data.events.length === 0}
				<div class="rounded-xl border border-outline-variant bg-surface-container-lowest p-16 text-center">
					<div class="mx-auto flex h-16 w-16 items-center justify-center rounded-2xl bg-surface-container-low">
						<Calendar size={32} class="text-on-surface-variant" />
					</div>
					<h3 class="mt-4 text-headline-md text-fg font-semibold">No events found</h3>
					<p class="mt-2 text-body-md text-on-surface-variant max-w-sm mx-auto">
						There are no upcoming events matching your criteria.
					</p>
					<div class="mt-6 flex items-center justify-center gap-3">
						<Button variant="primary" size="lg" onclick={handleCreateEvent}>
							Create your first event
						</Button>
					</div>
				</div>
			{:else}
				<div class="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6 animate-fade-in">
					{#each data.events as event (event.id)}
						<EventCard {event} onRegister={handleRegister} />
					{/each}
				</div>

				<div class="mt-10 flex justify-center">
					<button class="bg-surface-container-lowest border border-outline-variant px-8 py-3 rounded-lg font-bold text-fg hover:bg-surface-container-low transition-colors text-label-md">
						Load More Events
					</button>
				</div>
			{/if}
		</div>
	</div>
</section>

<!-- Footer -->
<footer class="bg-surface-container-lowest border-t border-outline-variant/60">
	<div class="flex flex-col md:flex-row justify-between items-center py-12 px-6 max-w-[1440px] mx-auto gap-6">
		<div class="flex flex-col items-center md:items-start gap-3">
			<a href="/" class="flex items-center gap-2">
				<div class="flex h-7 w-7 items-center justify-center rounded-md bg-primary text-on-primary text-xs font-bold">
					O
				</div>
				<span class="text-headline-md font-bold text-fg">OpenMeet</span>
			</a>
			<p class="text-body-md text-on-surface-variant max-w-xs text-center md:text-left">
				The leading platform for discovering and managing premium events globally.
			</p>
		</div>
		<div class="flex gap-8">
			<a href="/" class="text-body-md text-on-surface-variant hover:text-primary transition-colors">About</a>
			<a href="/" class="text-body-md text-on-surface-variant hover:text-primary transition-colors">Contact</a>
			<a href="/" class="text-body-md text-on-surface-variant hover:text-primary transition-colors">Terms</a>
			<a href="/" class="text-body-md text-on-surface-variant hover:text-primary transition-colors">Privacy</a>
		</div>
		<p class="text-body-md text-on-surface-variant">
			&copy; {new Date().getFullYear()} OpenMeet. All rights reserved.
		</p>
	</div>
</footer>
