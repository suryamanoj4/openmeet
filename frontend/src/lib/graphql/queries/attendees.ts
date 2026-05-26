export const ATTENDEES = `
	query Attendees($event_id: UUID, $limit: Int, $skip: Int) {
		attendees(ticketId: $event_id, limit: $limit, skip: $skip) {
			id
			first_name: firstName
			last_name: lastName
			email
			phone
			company
			check_in_status: checkInStatus
			check_in_at: checkInAt
			ticket_id: ticketId
		}
	}
`;

export const SEARCH_ATTENDEES = `
	query SearchAttendees($event_id: UUID!, $query: String!) {
		search_attendees: searchAttendees(eventId: $event_id, query: $query) {
			id
			first_name: firstName
			last_name: lastName
			email
			check_in_status: checkInStatus
			ticket_id: ticketId
		}
	}
`;

export const CHECK_IN_ATTENDEE = `
	mutation CheckInAttendee($attendee_id: UUID!, $checked_in_by: UUID!) {
		check_in_attendee: checkInAttendee(attendeeId: $attendee_id, checkedInBy: $checked_in_by) {
			id
			check_in_status: checkInStatus
			check_in_at: checkInAt
		}
	}
`;

export const UNDO_CHECK_IN = `
	mutation UndoCheckIn($attendee_id: UUID!) {
		undo_attendee_check_in: undoAttendeeCheckIn(attendeeId: $attendee_id) {
			id
			check_in_status: checkInStatus
		}
	}
`;
