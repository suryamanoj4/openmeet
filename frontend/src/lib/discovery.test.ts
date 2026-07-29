import assert from 'node:assert/strict';
import test from 'node:test';

import {
	buildDiscoveryUrl,
	clearDiscoveryUrl,
	filterEvents,
	getCategories,
	getVenues,
	groupEventsByDay
} from './discovery.ts';
import type { Event } from './graphql/types.ts';

function event(overrides: Partial<Event>): Event {
	return {
		id: 'event-id',
		organization_id: null,
		name: 'OpenMeet Event',
		slug: 'openmeet-event',
		event_type: 'conference',
		status: 'published',
		visibility: 'public',
		start_date: '2026-08-10T10:00:00Z',
		end_date: '2026-08-10T12:00:00Z',
		timezone: 'UTC',
		is_online: false,
		min_tickets_per_order: 1,
		max_tickets_per_order: 10,
		created_at: '2026-07-01T00:00:00Z',
		updated_at: '2026-07-01T00:00:00Z',
		...overrides
	};
}

test('event search matches useful public event details case-insensitively', () => {
	const events = [
		event({ id: '1', name: 'Frontend Summit', venue_city: 'Pune' }),
		event({ id: '2', name: 'Jazz Night', description: 'Live music downtown' })
	];

	assert.deepEqual(
		filterEvents(events, { q: 'PUNE' }).map((item) => item.id),
		['1']
	);
	assert.deepEqual(
		filterEvents(events, { q: 'live music' }).map((item) => item.id),
		['2']
	);
});

test('category and venue discovery options come from actual events', () => {
	const events = [
		event({ id: '1', event_type: 'workshop', venue_city: 'Pune' }),
		event({ id: '2', event_type: 'conference', is_online: true }),
		event({ id: '3', event_type: 'workshop', venue_city: 'Pune' }),
		event({ id: '4', event_type: 'meetup' })
	];

	assert.deepEqual(getCategories(events), ['conference', 'meetup', 'workshop']);
	assert.deepEqual(getVenues(events), ['Online', 'Other / TBD', 'Pune']);
});

test('category and venue filters combine to narrow discovery results', () => {
	const events = [
		event({ id: '1', event_type: 'workshop', venue_city: 'Pune' }),
		event({ id: '2', event_type: 'conference', venue_city: 'Pune' }),
		event({ id: '3', event_type: 'workshop', is_online: true })
	];

	assert.deepEqual(
		filterEvents(events, { category: 'workshop', venue: 'Pune' }).map(
			(item) => item.id
		),
		['1']
	);
});

test('calendar filters use local calendar boundaries', () => {
	const now = new Date(2026, 6, 29, 12);
	const events = [
		event({ id: 'today', start_date: new Date(2026, 6, 29, 18).toISOString() }),
		event({ id: 'tomorrow', start_date: new Date(2026, 6, 30, 10).toISOString() }),
		event({ id: 'next-month', start_date: new Date(2026, 7, 12, 10).toISOString() })
	];

	assert.deepEqual(
		filterEvents(events, { date: 'today' }, now).map((item) => item.id),
		['today']
	);
	assert.deepEqual(
		filterEvents(events, { date: 'month' }, now).map((item) => item.id),
		['next-month']
	);
});

test('date sorting and calendar grouping are chronological', () => {
	const events = [
		event({ id: 'later', name: 'Later', start_date: '2026-08-12T10:00:00Z' }),
		event({ id: 'earlier', name: 'Earlier', start_date: '2026-08-10T10:00:00Z' }),
		event({ id: 'same-day', name: 'Same day', start_date: '2026-08-10T18:00:00Z' })
	];

	const sorted = filterEvents(events, { sort: 'date' });
	assert.deepEqual(sorted.map((item) => item.id), ['earlier', 'same-day', 'later']);
	assert.deepEqual(
		groupEventsByDay(sorted).map((group) => group.events.map((item) => item.id)),
		[['earlier', 'same-day'], ['later']]
	);
});

test('discovery URLs preserve active filters and clear them predictably', () => {
	const current = new URLSearchParams('view=categories&q=music&category=meetup');

	assert.equal(
		buildDiscoveryUrl(current, { category: null, venue: 'Online' }, 'venues'),
		'/?view=venues&q=music&venue=Online#discover'
	);
	assert.equal(clearDiscoveryUrl('calendar'), '/?view=calendar&sort=date#discover');
});
