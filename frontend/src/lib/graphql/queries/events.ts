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

export const TRANSFER_EVENT_OWNERSHIP = `
	mutation TransferEventOwnership($event_id: UUID!, $new_owner_id: UUID!) {
		transfer_event_ownership: transferEventOwnership(eventId: $event_id, newOwnerId: $new_owner_id)
	}
`;

export const EVENT_PAGE = `
	query EventPage($event_id: UUID!) {
		event_page: eventPage(eventId: $event_id) {
			id
			event_id: eventId
			blocks
			is_published: isPublished
			published_at: publishedAt
		}
	}
`;

export const SAVE_EVENT_PAGE = `
	mutation SaveEventPage($event_id: UUID!, $input: UpdateEventPageInput!) {
		save_event_page: saveEventPage(eventId: $event_id, input: $input) {
			id
			blocks
			is_published: isPublished
		}
	}
`;

export const PUBLISH_EVENT_PAGE = `
	mutation PublishEventPage($event_id: UUID!) {
		publish_event_page: publishEventPage(eventId: $event_id) {
			id
			is_published: isPublished
		}
	}
`;

export const UNPUBLISH_EVENT_PAGE = `
	mutation UnpublishEventPage($event_id: UUID!) {
		unpublish_event_page: unpublishEventPage(eventId: $event_id) {
			id
			is_published: isPublished
		}
	}
`;
