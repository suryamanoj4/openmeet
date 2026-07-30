import assert from 'node:assert/strict';
import test from 'node:test';

import { ATTENDEES } from './queries/attendees.ts';
import { PUBLIC_EVENT, RESOLVE_PUBLIC_EVENT_SLUG } from './queries/events.ts';

test('attendee listing sends eventId instead of treating an event as a ticket', () => {
	assert.match(ATTENDEES, /attendees\(eventId: \$event_id/);
	assert.doesNotMatch(ATTENDEES, /ticketId: \$event_id/);
});

test('public event queries expose the safe slug resolution flow', () => {
	assert.match(RESOLVE_PUBLIC_EVENT_SLUG, /resolvePublicEventSlug/);
	assert.match(PUBLIC_EVENT, /publicEvent\(id: \$id, slug: \$slug\)/);
});
