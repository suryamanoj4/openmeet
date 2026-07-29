export interface EventFormValues {
	organization_id?: string;
	name: string;
	slug: string;
	description: string;
	event_type: string;
	start_date: string;
	end_date: string;
	venue_city: string;
	is_online: boolean;
	cover_image_url: string;
}

export interface CreateEventInput {
	organizationId: string | null;
	name: string;
	slug: string;
	description: string | null;
	eventType: string;
	startDate: string;
	endDate: string;
	venueCity: string | null;
	isOnline: boolean;
	coverImageUrl: string | null;
}

export interface UpdateEventFormValues {
	name: string;
	slug: string;
	description: string;
	event_type: string;
	venue_city: string;
	is_online: boolean;
	cover_image_url: string;
}

export interface UpdateEventInput {
	name: string;
	description: string | null;
	eventType: string;
	venueCity: string | null;
	isOnline: boolean;
	coverImageUrl: string | null;
}

export function toCreateEventInput(values: EventFormValues): CreateEventInput {
	return {
		organizationId: values.organization_id || null,
		name: values.name,
		slug: values.slug,
		description: values.description || null,
		eventType: values.event_type,
		startDate: new Date(values.start_date).toISOString(),
		endDate: new Date(values.end_date).toISOString(),
		venueCity: values.venue_city || null,
		isOnline: values.is_online,
		coverImageUrl: values.cover_image_url || null
	};
}

export function toUpdateEventInput(values: UpdateEventFormValues): UpdateEventInput {
	return {
		name: values.name,
		description: values.description || null,
		eventType: values.event_type,
		venueCity: values.venue_city || null,
		isOnline: values.is_online,
		coverImageUrl: values.cover_image_url || null
	};
}
