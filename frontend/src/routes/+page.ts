import { graphqlClient } from '$lib/graphql/client';
import { PUBLIC_EVENTS } from '$lib/graphql/queries/events';
import type { Event } from '$lib/graphql/types';

export interface HomePageData {
	events: Event[];
	error: string | null;
}

interface EventsResponse {
	public_events: Event[];
}

export async function load(): Promise<HomePageData> {
	try {
		const result = await graphqlClient
			.query<EventsResponse>(
				PUBLIC_EVENTS,
				{ limit: 24 }
			)
			.toPromise();

		if (result.error) {
			return { events: [], error: result.error.message };
		}

		const events = result.data?.public_events ?? [];

		return { events, error: null };
	} catch (err) {
		return { events: [], error: err instanceof Error ? err.message : 'Failed to load events' };
	}
}
