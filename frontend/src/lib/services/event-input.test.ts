import assert from 'node:assert/strict';
import test from 'node:test';

import { toCreateEventInput, toUpdateEventInput } from './event-input.ts';

test('create-event form values are mapped to the GraphQL input contract', () => {
	assert.deepEqual(
		toCreateEventInput({
			organization_id: undefined,
			name: 'Community Meetup',
			slug: 'community-meetup',
			description: '',
			event_type: 'meetup',
			start_date: '2026-08-01T10:00',
			end_date: '2026-08-01T12:00',
			venue_city: '',
			is_online: false,
			cover_image_url: ''
		}),
		{
			organizationId: null,
			name: 'Community Meetup',
			slug: 'community-meetup',
			description: null,
			eventType: 'meetup',
			startDate: new Date('2026-08-01T10:00').toISOString(),
			endDate: new Date('2026-08-01T12:00').toISOString(),
			venueCity: null,
			isOnline: false,
			coverImageUrl: null
		}
	);
});

test('edit-event form values omit immutable fields and use GraphQL field names', () => {
	assert.deepEqual(
		toUpdateEventInput({
			name: 'Updated Meetup',
			slug: 'ignored-slug',
			description: 'Updated description',
			event_type: 'workshop',
			venue_city: 'Pune',
			is_online: true,
			cover_image_url: 'https://example.com/cover.jpg'
		}),
		{
			name: 'Updated Meetup',
			description: 'Updated description',
			eventType: 'workshop',
			venueCity: 'Pune',
			isOnline: true,
			coverImageUrl: 'https://example.com/cover.jpg'
		}
	);
});
