import { graphqlClient } from '$lib/graphql/client';
import { requireMutationResult } from '$lib/graphql/result';
import { ATTENDEES, SEARCH_ATTENDEES, CHECK_IN_ATTENDEE, UNDO_CHECK_IN } from '$lib/graphql/queries/attendees';

interface AttendeeSummary { id: string; first_name: string; last_name: string; email: string; check_in_status: string; check_in_at?: string; ticket_id?: string }

export async function listAttendees(eventId?: string): Promise<AttendeeSummary[]> {
	const r = await graphqlClient.query<{ attendees: AttendeeSummary[] }>(ATTENDEES, { event_id: eventId || null }).toPromise();
	return requireMutationResult(r, 'attendees', 'Failed to load attendees');
}

export async function searchAttendees(eventId: string, query: string): Promise<AttendeeSummary[]> {
	const r = await graphqlClient.query<{ search_attendees: AttendeeSummary[] }>(SEARCH_ATTENDEES, { event_id: eventId, query }).toPromise();
	return requireMutationResult(r, 'search_attendees', 'Failed to search attendees');
}

export async function checkIn(attendeeId: string, _checkedInBy: string): Promise<{ id: string; check_in_status: string; check_in_at?: string } | null> {
	const r = await graphqlClient.mutation<{ check_in_attendee: { id: string; check_in_status: string; check_in_at?: string } }>(CHECK_IN_ATTENDEE, { attendee_id: attendeeId }).toPromise();
	return requireMutationResult(r, 'check_in_attendee', 'Failed to check in attendee');
}

export async function undoCheckIn(attendeeId: string): Promise<{ id: string; check_in_status: string } | null> {
	const r = await graphqlClient.mutation<{ undo_attendee_check_in: { id: string; check_in_status: string } }>(UNDO_CHECK_IN, { attendee_id: attendeeId }).toPromise();
	return requireMutationResult(r, 'undo_attendee_check_in', 'Failed to undo attendee check-in');
}
