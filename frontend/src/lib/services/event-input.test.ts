import assert from 'node:assert/strict';
import test from 'node:test';

import {
	minimumFutureDatetime,
	toCreateEventInput,
	toDatetimeLocalValue,
	toUpdateEventInput,
	validateEventSchedule,
	validateRegistrationWindow
} from './event-input.ts';

const extendedFields = {
	timezone: 'Asia/Kolkata',
	venue_name: 'Community Hall',
	venue_address: '1 Main Road',
	venue_city: '',
	venue_country: 'India',
	is_online: false,
	online_url: '',
	max_attendees: 100,
	min_tickets_per_order: 1,
	max_tickets_per_order: 5,
	registration_start: '2026-07-31T10:00',
	registration_end: '2026-08-01T09:00',
	cover_image_url: '',
	banner_image_url: ''
};

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
			...extendedFields
		}),
		{
			organizationId: null,
			name: 'Community Meetup',
			slug: 'community-meetup',
			description: null,
			eventType: 'meetup',
			startDate: new Date('2026-08-01T10:00').toISOString(),
			endDate: new Date('2026-08-01T12:00').toISOString(),
			timezone: 'Asia/Kolkata',
			venueName: 'Community Hall',
			venueAddress: { formatted: '1 Main Road' },
			venueCity: null,
			venueCountry: 'India',
			isOnline: false,
			onlineUrl: null,
			maxAttendees: 100,
			minTicketsPerOrder: 1,
			maxTicketsPerOrder: 5,
			registrationStart: new Date('2026-07-31T10:00').toISOString(),
			registrationEnd: new Date('2026-08-01T09:00').toISOString(),
			coverImageUrl: null,
			bannerImageUrl: null,
			settings: null
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
			start_date: '2026-08-02T10:00',
			end_date: '2026-08-02T12:00',
			...extendedFields,
			venue_city: 'Pune',
			is_online: true,
			cover_image_url: 'https://example.com/cover.jpg'
		}),
		{
			name: 'Updated Meetup',
			description: 'Updated description',
			eventType: 'workshop',
			startDate: new Date('2026-08-02T10:00').toISOString(),
			endDate: new Date('2026-08-02T12:00').toISOString(),
			timezone: 'Asia/Kolkata',
			venueName: 'Community Hall',
			venueAddress: { formatted: '1 Main Road' },
			venueCity: 'Pune',
			venueCountry: 'India',
			isOnline: true,
			onlineUrl: null,
			maxAttendees: 100,
			minTicketsPerOrder: 1,
			maxTicketsPerOrder: 5,
			registrationStart: new Date('2026-07-31T10:00').toISOString(),
			registrationEnd: new Date('2026-08-01T09:00').toISOString(),
			coverImageUrl: 'https://example.com/cover.jpg',
			bannerImageUrl: null,
			settings: null
		}
	);
});

test('registration windows must be future, ordered, and before the event', () => {
	const now = new Date('2026-07-30T09:00:00Z');
	assert.equal(
		validateRegistrationWindow(
			'2026-07-30T08:00:00Z',
			'2026-07-31T08:00:00Z',
			'2026-08-01T08:00:00Z',
			'2026-08-01T10:00:00Z',
			now
		),
		'Registration start must be in the future.'
	);
	assert.equal(
		validateRegistrationWindow(
			'2026-08-02T08:00:00Z',
			'',
			'2026-08-01T08:00:00Z',
			'2026-08-01T10:00:00Z',
			now
		),
		'Registration must open before the event starts.'
	);
});

test('datetime helpers produce local input values and a one-minute future minimum', () => {
	const now = new Date('2026-08-01T09:00:00Z');
	assert.equal(
		new Date(minimumFutureDatetime(now)).getTime(),
		now.getTime() + 60_000
	);
	assert.equal(toDatetimeLocalValue('not-a-date'), '');
});

test('event schedule validation rejects past and inverted ranges', () => {
	const now = new Date('2026-08-01T09:00:00.000Z');

	assert.equal(
		validateEventSchedule('2026-08-01T08:00:00.000Z', '2026-08-01T10:00:00.000Z', now),
		'Start date must be in the future.'
	);
	assert.equal(
		validateEventSchedule('2026-08-01T12:00:00.000Z', '2026-08-01T11:00:00.000Z', now),
		'End date must be after the start date.'
	);
	assert.equal(
		validateEventSchedule('2026-08-01T10:00:00.000Z', '2026-08-01T11:00:00.000Z', now),
		null
	);
});
