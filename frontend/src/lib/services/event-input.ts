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
	start_date: string;
	end_date: string;
	venue_city: string;
	is_online: boolean;
	cover_image_url: string;
}

export interface UpdateEventInput {
	name: string;
	description: string | null;
	eventType: string;
	startDate: string;
	endDate: string;
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

export function toDatetimeLocalValue(value: string): string {
	const date = new Date(value);
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
		venueCity: values.venue_city || null,
		isOnline: values.is_online,
		coverImageUrl: values.cover_image_url || null
	};
}
