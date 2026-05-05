import { graphqlClient } from '$lib/graphql/client';
import type { Event } from '$lib/graphql/types';

export interface HomePageData {
	events: Event[];
	error: string | null;
}

interface EventsResponse {
	events: Event[];
}

export async function load(): Promise<HomePageData> {
	try {
		const result = await graphqlClient
			.query<EventsResponse>(
				`
				query PublicEvents($limit: Int!) {
					events(limit: $limit) {
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
						online_url: onlineUrl
						cover_image_url: coverImageUrl
						banner_image_url: bannerImageUrl
						max_attendees: maxAttendees
						min_tickets_per_order: minTicketsPerOrder
						max_tickets_per_order: maxTicketsPerOrder
						organization_id: organizationId
					}
				}
				`,
				{ limit: 24 }
			)
			.toPromise();

		if (result.error) {
			return { events: [], error: result.error.message };
		}

		const events = (result.data?.events ?? []).filter(
			(e) => e.status === 'published'
		);

		return { events, error: null };
	} catch (err) {
		return { events: [], error: err instanceof Error ? err.message : 'Failed to load events' };
	}
}
