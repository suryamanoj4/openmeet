import { graphqlClient } from '$lib/graphql/client';
import { ATTENDEES, SEARCH_ATTENDEES, CHECK_IN_ATTENDEE, UNDO_CHECK_IN } from '$lib/graphql/queries/attendees';

interface AttendeeSummary { id: string; first_name: string; last_name: string; email: string; check_in_status: string; check_in_at?: string; ticket_id?: string }

export async function listAttendees(eventId?: string): Promise<AttendeeSummary[]> {
	const r = await graphqlClient.query<{ attendees: AttendeeSummary[] }>(ATTENDEES, { event_id: eventId || null }).toPromise();
	return r.data?.attendees ?? [];
}

export async function searchAttendees(eventId: string, query: string): Promise<AttendeeSummary[]> {
	const r = await graphqlClient.query<{ search_attendees: AttendeeSummary[] }>(SEARCH_ATTENDEES, { event_id: eventId, query }).toPromise();
	return r.data?.search_attendees ?? [];
}

export async function checkIn(attendeeId: string, checkedInBy: string): Promise<{ id: string; check_in_status: string; check_in_at?: string } | null> {
	const r = await graphqlClient.mutation<{ check_in_attendee: { id: string; check_in_status: string; check_in_at?: string } }>(CHECK_IN_ATTENDEE, { attendee_id: attendeeId, checked_in_by: checkedInBy }).toPromise();
	return r.data?.check_in_attendee ?? null;
}

export async function undoCheckIn(attendeeId: string): Promise<{ id: string; check_in_status: string } | null> {
	const r = await graphqlClient.mutation<{ undo_attendee_check_in: { id: string; check_in_status: string } }>(UNDO_CHECK_IN, { attendee_id: attendeeId }).toPromise();
	return r.data?.undo_attendee_check_in ?? null;
}
