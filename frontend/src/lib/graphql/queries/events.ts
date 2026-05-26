export const EVENTS = `
	query Events($limit: Int, $skip: Int) {
		events(limit: $limit, skip: $skip) {
			id
			name
			slug
			description
			event_type: eventType
			status
			visibility
			start_date: startDate
			end_date: endDate
			timezone
			venue_name: venueName
			venue_city: venueCity
			venue_country: venueCountry
			is_online: isOnline
			cover_image_url: coverImageUrl
			max_attendees: maxAttendees
			min_tickets_per_order: minTicketsPerOrder
			max_tickets_per_order: maxTicketsPerOrder
			organization_id: organizationId
		}
	}
`;

export const EVENT = `
	query Event($id: UUID!) {
		event(id: $id) {
			id
			name
			slug
			description
			event_type: eventType
			status
			visibility
			start_date: startDate
			end_date: endDate
			timezone
			venue_name: venueName
			venue_address: venueAddress
			venue_city: venueCity
			venue_country: venueCountry
			is_online: isOnline
			online_url: onlineUrl
			max_attendees: maxAttendees
			min_tickets_per_order: minTicketsPerOrder
			max_tickets_per_order: maxTicketsPerOrder
			registration_start: registrationStart
			registration_end: registrationEnd
			cover_image_url: coverImageUrl
			banner_image_url: bannerImageUrl
			organization_id: organizationId
		}
	}
`;

export const EVENT_BY_SLUG = `
	query EventBySlug($organization_id: UUID!, $slug: String!) {
		event_by_slug(organizationId: $organization_id, slug: $slug) {
			id
			name
			slug
			description
			event_type: eventType
			status
			visibility
			start_date: startDate
			end_date: endDate
			timezone
			venue_name: venueName
			venue_address: venueAddress
			venue_city: venueCity
			venue_country: venueCountry
			is_online: isOnline
			online_url: onlineUrl
			max_attendees: maxAttendees
			cover_image_url: coverImageUrl
			banner_image_url: bannerImageUrl
			organization_id: organizationId
		}
	}
`;

export const EVENT_TICKETS = `
	query EventTickets($event_id: UUID!) {
		event_tickets(eventId: $event_id) {
			id
			name
			description
			price
			currency
			quantity
			sold_quantity: soldQuantity
			min_per_order: minPerOrder
			max_per_order: maxPerOrder
			sale_start: saleStart
			sale_end: saleEnd
			is_active: isActive
		}
	}
`;

export const AVAILABLE_TICKETS = `
	query AvailableTickets($event_id: UUID!) {
		available_tickets(eventId: $event_id) {
			id
			name
			description
			price
			currency
			quantity
			sold_quantity: soldQuantity
			min_per_order: minPerOrder
			max_per_order: maxPerOrder
		}
	}
`;

export const CREATE_EVENT = `
	mutation CreateEvent($input: CreateEventInput!) {
		create_event: createEvent(input: $input) {
			id
			name
			slug
		}
	}
`;

export const UPDATE_EVENT = `
	mutation UpdateEvent($id: UUID!, $input: UpdateEventInput!) {
		update_event: updateEvent(id: $id, input: $input) {
			id
			name
			slug
		}
	}
`;

export const DELETE_EVENT = `
	mutation DeleteEvent($id: UUID!) {
		delete_event: deleteEvent(id: $id)
	}
`;

export const ADD_EVENT_ORGANIZER = `
	mutation AddEventOrganizer($event_id: UUID!, $user_id: UUID!) {
		add_event_organizer: addEventOrganizer(eventId: $event_id, userId: $user_id) {
			id
			user_id: userId
			role
			is_owner: isOwner
		}
	}
`;
