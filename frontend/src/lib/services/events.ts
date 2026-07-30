import { graphqlClient } from '$lib/graphql/client';
import { requireMutationResult } from '$lib/graphql/result';
import { EVENTS, EVENT, EVENT_TICKETS, CREATE_EVENT, UPDATE_EVENT, DELETE_EVENT, ADD_EVENT_ORGANIZER } from '$lib/graphql/queries/events';
import type { Event } from '$lib/graphql/types';
import type { CreateEventInput, UpdateEventInput } from '$lib/services/event-input';

interface EventsResponse { events: Event[] }
interface EventResponse { event: Event | null }
interface TicketsResponse { event_tickets: { id: string; name: string; price: number; currency: string; quantity: number; sold_quantity: number }[] }

export async function listEvents(limit = 50, skip = 0): Promise<Event[]> {
	const r = await graphqlClient.query<EventsResponse>(EVENTS, { limit, skip }).toPromise();
	return requireMutationResult(r, 'events', 'Failed to load events');
}

export async function getEvent(id: string): Promise<Event | null> {
	const r = await graphqlClient.query<EventResponse>(EVENT, { id }).toPromise();
	if (r.error) throw new Error(r.error.message);
	return r.data?.event ?? null;
}

export async function getEventTickets(eventId: string): Promise<TicketsResponse['event_tickets']> {
	const r = await graphqlClient.query<TicketsResponse>(EVENT_TICKETS, { event_id: eventId }).toPromise();
	return requireMutationResult(r, 'event_tickets', 'Failed to load tickets');
}

export async function createEvent(input: CreateEventInput): Promise<{ id: string; name: string }> {
	const r = await graphqlClient.mutation<{ create_event: { id: string; name: string } }>(CREATE_EVENT, { input }).toPromise();
	return requireMutationResult(r, 'create_event', 'Failed to create event');
}

export async function updateEvent(id: string, input: UpdateEventInput): Promise<{ id: string; name: string }> {
	const r = await graphqlClient.mutation<{ update_event: { id: string; name: string } }>(UPDATE_EVENT, { id, input }).toPromise();
	return requireMutationResult(r, 'update_event', 'Failed to update event');
}

export async function deleteEvent(id: string): Promise<boolean> {
	const r = await graphqlClient.mutation<{ delete_event: boolean }>(DELETE_EVENT, { id }).toPromise();
	return requireMutationResult(r, 'delete_event', 'Failed to delete event');
}

export async function addOrganizer(eventId: string, userId: string): Promise<boolean> {
	const r = await graphqlClient.mutation<{ add_event_organizer: { id: string } }>(ADD_EVENT_ORGANIZER, { event_id: eventId, user_id: userId }).toPromise();
	return !!requireMutationResult(r, 'add_event_organizer', 'Failed to add organizer');
}
