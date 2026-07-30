import type { Event } from './graphql/types';

export type DiscoveryView = 'explore' | 'categories' | 'calendar' | 'venues';
export type DiscoverySort = 'relevant' | 'date' | 'name';

export interface DiscoveryFilters {
	q?: string;
	category?: string;
	date?: string;
	venue?: string;
	sort?: DiscoverySort;
}

export function buildDiscoveryUrl(
	current: URLSearchParams,
	changes: Record<string, string | null>,
	view: DiscoveryView
): string {
	const params = new URLSearchParams(current);
	params.set('view', view);
	for (const [key, value] of Object.entries(changes)) {
		if (value) params.set(key, value);
		else params.delete(key);
	}
	return `/?${params.toString()}#discover`;
}

export function clearDiscoveryUrl(view: DiscoveryView): string {
	const params = new URLSearchParams({ view });
	if (view === 'calendar') params.set('sort', 'date');
	return `/?${params.toString()}#discover`;
}

export function getEventVenue(event: Event): string {
	if (event.is_online) return 'Online';
	return event.venue_city?.trim() || 'Other / TBD';
}

export function getCategories(events: Event[]): string[] {
	return [...new Set(events.map((event) => event.event_type).filter(Boolean))].sort();
}

export function getVenues(events: Event[]): string[] {
	return [...new Set(events.map(getEventVenue))].sort();
}

export interface EventDayGroup {
	key: string;
	date: Date;
	events: Event[];
}

export function groupEventsByDay(events: Event[]): EventDayGroup[] {
	const groups = new Map<string, EventDayGroup>();

	for (const event of events) {
		const date = new Date(event.start_date);
		const key = [
			date.getFullYear(),
			String(date.getMonth() + 1).padStart(2, '0'),
			String(date.getDate()).padStart(2, '0')
		].join('-');
		const group = groups.get(key) ?? { key, date: startOfDay(date), events: [] };
		group.events.push(event);
		groups.set(key, group);
	}

	return [...groups.values()].sort((a, b) => a.date.getTime() - b.date.getTime());
}

function startOfDay(value: Date): Date {
	return new Date(value.getFullYear(), value.getMonth(), value.getDate());
}

function matchesDateFilter(event: Event, filter: string | undefined, now: Date): boolean {
	if (!filter) return true;

	const eventDate = new Date(event.start_date);
	const today = startOfDay(now);
	let start = today;
	let end = new Date(today);

	if (filter === 'tomorrow') {
		start = new Date(today);
		start.setDate(start.getDate() + 1);
		end = new Date(start);
		end.setDate(end.getDate() + 1);
	} else if (filter === 'week') {
		const daysUntilMonday = (8 - end.getDay()) % 7 || 7;
		end.setDate(end.getDate() + daysUntilMonday);
	} else if (filter === 'month') {
		start = new Date(today.getFullYear(), today.getMonth() + 1, 1);
		end = new Date(today.getFullYear(), today.getMonth() + 2, 1);
	} else {
		end.setDate(end.getDate() + 1);
	}

	return eventDate >= start && eventDate < end;
}

export function filterEvents(
	events: Event[],
	filters: DiscoveryFilters,
	now = new Date()
): Event[] {
	const query = filters.q?.trim().toLowerCase();
	const category = filters.category?.trim().toLowerCase();
	const venue = filters.venue?.trim().toLowerCase();

	const filtered = events.filter((event) =>
		(!query ||
			[
				event.name,
				event.description,
				event.event_type,
				event.venue_name,
				event.venue_city,
				event.venue_country,
				event.is_online ? 'online' : ''
			]
				.filter(Boolean)
				.some((value) => value!.toLowerCase().includes(query))) &&
		(!category || event.event_type.toLowerCase() === category) &&
		(!venue || getEventVenue(event).toLowerCase().includes(venue)) &&
		matchesDateFilter(event, filters.date, now)
	);

	if (filters.sort === 'date') {
		return filtered.sort(
			(a, b) => new Date(a.start_date).getTime() - new Date(b.start_date).getTime()
		);
	}
	if (filters.sort === 'name') {
		return filtered.sort((a, b) => a.name.localeCompare(b.name));
	}
	return filtered;
}
