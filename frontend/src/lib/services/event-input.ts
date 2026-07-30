export interface EventFormValues {
	organization_id?: string;
	name: string;
	slug: string;
	description: string;
	event_type: string;
	start_date: string;
	end_date: string;
	timezone: string;
	venue_name: string;
	venue_address: string;
	venue_city: string;
	venue_country: string;
	is_online: boolean;
	online_url: string;
	max_attendees: number | null;
	min_tickets_per_order: number;
	max_tickets_per_order: number;
	registration_start: string;
	registration_end: string;
	cover_image_url: string;
	banner_image_url: string;
	settings?: Record<string, unknown>;
}

export interface CreateEventInput {
	organizationId: string | null;
	name: string;
	slug: string;
	description: string | null;
	eventType: string;
	startDate: string;
	endDate: string;
	timezone: string;
	venueName: string | null;
	venueAddress: Record<string, string> | null;
	venueCity: string | null;
	venueCountry: string | null;
	isOnline: boolean;
	onlineUrl: string | null;
	maxAttendees: number | null;
	minTicketsPerOrder: number;
	maxTicketsPerOrder: number;
	registrationStart: string | null;
	registrationEnd: string | null;
	coverImageUrl: string | null;
	bannerImageUrl: string | null;
	settings: Record<string, unknown> | null;
}

export interface UpdateEventFormValues {
	name: string;
	slug: string;
	description: string;
	event_type: string;
	start_date: string;
	end_date: string;
	timezone: string;
	venue_name: string;
	venue_address: string;
	venue_city: string;
	venue_country: string;
	is_online: boolean;
	online_url: string;
	max_attendees: number | null;
	min_tickets_per_order: number;
	max_tickets_per_order: number;
	registration_start: string;
	registration_end: string;
	cover_image_url: string;
	banner_image_url: string;
	settings?: Record<string, unknown>;
}

export interface UpdateEventInput {
	name: string;
	description: string | null;
	eventType: string;
	startDate: string;
	endDate: string;
	timezone: string;
	venueName: string | null;
	venueAddress: Record<string, string> | null;
	venueCity: string | null;
	venueCountry: string | null;
	isOnline: boolean;
	onlineUrl: string | null;
	maxAttendees: number | null;
	minTicketsPerOrder: number;
	maxTicketsPerOrder: number;
	registrationStart: string | null;
	registrationEnd: string | null;
	coverImageUrl: string | null;
	bannerImageUrl: string | null;
	settings: Record<string, unknown> | null;
}

function optionalDatetime(value: string): string | null {
	return value ? new Date(value).toISOString() : null;
}

function optionalAddress(value: string): Record<string, string> | null {
	return value.trim() ? { formatted: value.trim() } : null;
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
		timezone: values.timezone,
		venueName: values.venue_name || null,
		venueAddress: optionalAddress(values.venue_address),
		venueCity: values.venue_city || null,
		venueCountry: values.venue_country || null,
		isOnline: values.is_online,
		onlineUrl: values.online_url || null,
		maxAttendees: values.max_attendees,
		minTicketsPerOrder: values.min_tickets_per_order,
		maxTicketsPerOrder: values.max_tickets_per_order,
		registrationStart: optionalDatetime(values.registration_start),
		registrationEnd: optionalDatetime(values.registration_end),
		coverImageUrl: values.cover_image_url || null,
		bannerImageUrl: values.banner_image_url || null,
		settings: values.settings ?? null
	};
}

export function validateEventSchedule(
	startDate: string,
	endDate: string,
	now = new Date(),
	allowPastStart = false
): string | null {
	const start = new Date(startDate);
	const end = new Date(endDate);
	if (Number.isNaN(start.getTime()) || Number.isNaN(end.getTime())) {
		return 'Enter a valid start and end date.';
	}
	if (!allowPastStart && start <= now) return 'Start date must be in the future.';
	if (allowPastStart && end <= now) return 'End date must be in the future.';
	if (end <= start) return 'End date must be after the start date.';
	return null;
}

export function validateRegistrationWindow(
	registrationStart: string,
	registrationEnd: string,
	eventStart: string,
	eventEnd: string,
	now = new Date(),
	requireFutureStart = true
): string | null {
	const start = registrationStart ? new Date(registrationStart) : null;
	const end = registrationEnd ? new Date(registrationEnd) : null;
	const event = new Date(eventStart);
	const eventFinish = new Date(eventEnd);
	if (
		(start && Number.isNaN(start.getTime())) ||
		(end && Number.isNaN(end.getTime()))
	) {
		return 'Enter valid registration dates.';
	}
	if (start && requireFutureStart && start <= now) {
		return 'Registration start must be in the future.';
	}
	if (start && start > event) {
		return 'Registration must open before the event starts.';
	}
	if (start && end && end <= start) {
		return 'Registration end must be after registration start.';
	}
	if (end && end > eventFinish) {
		return 'Registration must close before the event ends.';
	}
	return null;
}

export function toDatetimeLocalValue(value: string): string {
	const date = new Date(value);
	if (Number.isNaN(date.getTime())) return '';
	const offset = date.getTimezoneOffset() * 60_000;
	return new Date(date.getTime() - offset).toISOString().slice(0, 16);
}

export function minimumFutureDatetime(now = new Date()): string {
	return toDatetimeLocalValue(new Date(now.getTime() + 60_000).toISOString());
}

export function toUpdateEventInput(values: UpdateEventFormValues): UpdateEventInput {
	return {
		name: values.name,
		description: values.description || null,
		eventType: values.event_type,
		startDate: new Date(values.start_date).toISOString(),
		endDate: new Date(values.end_date).toISOString(),
		timezone: values.timezone,
		venueName: values.venue_name || null,
		venueAddress: optionalAddress(values.venue_address),
		venueCity: values.venue_city || null,
		venueCountry: values.venue_country || null,
		isOnline: values.is_online,
		onlineUrl: values.online_url || null,
		maxAttendees: values.max_attendees,
		minTicketsPerOrder: values.min_tickets_per_order,
		maxTicketsPerOrder: values.max_tickets_per_order,
		registrationStart: optionalDatetime(values.registration_start),
		registrationEnd: optionalDatetime(values.registration_end),
		coverImageUrl: values.cover_image_url || null,
		bannerImageUrl: values.banner_image_url || null,
		settings: values.settings ?? null
	};
}
