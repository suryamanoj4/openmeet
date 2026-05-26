import { graphqlClient } from '$lib/graphql/client';
import { EVENTS, EVENT, EVENT_TICKETS, CREATE_EVENT, UPDATE_EVENT, DELETE_EVENT, ADD_EVENT_ORGANIZER } from '$lib/graphql/queries/events';
import type { Event } from '$lib/graphql/types';

interface EventsResponse { events: Event[] }
interface EventResponse { event: Event | null }
interface TicketsResponse { event_tickets: { id: string; name: string; price: number; currency: string; quantity: number; sold_quantity: number }[] }

export async function listEvents(limit = 50, skip = 0): Promise<Event[]> {
	const r = await graphqlClient.query<EventsResponse>(EVENTS, { limit, skip }).toPromise();
	return r.data?.events ?? [];
}

export async function getEvent(id: string): Promise<Event | null> {
	const r = await graphqlClient.query<EventResponse>(EVENT, { id }).toPromise();
	return r.data?.event ?? null;
}

export async function getEventTickets(eventId: string): Promise<TicketsResponse['event_tickets']> {
	const r = await graphqlClient.query<TicketsResponse>(EVENT_TICKETS, { event_id: eventId }).toPromise();
	return r.data?.event_tickets ?? [];
}

export async function createEvent(input: Record<string, unknown>): Promise<{ id: string; name: string } | null> {
	const r = await graphqlClient.mutation<{ create_event: { id: string; name: string } }>(CREATE_EVENT, { input }).toPromise();
	return r.data?.create_event ?? null;
}

export async function updateEvent(id: string, input: Record<string, unknown>): Promise<{ id: string; name: string } | null> {
	const r = await graphqlClient.mutation<{ update_event: { id: string; name: string } }>(UPDATE_EVENT, { id, input }).toPromise();
	return r.data?.update_event ?? null;
}

export async function deleteEvent(id: string): Promise<boolean> {
	const r = await graphqlClient.mutation<{ delete_event: boolean }>(DELETE_EVENT, { id }).toPromise();
	return r.data?.delete_event ?? false;
}

export async function addOrganizer(eventId: string, userId: string): Promise<boolean> {
	const r = await graphqlClient.mutation<{ add_event_organizer: { id: string } }>(ADD_EVENT_ORGANIZER, { event_id: eventId, user_id: userId }).toPromise();
	return !!r.data?.add_event_organizer;
}
