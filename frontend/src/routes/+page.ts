import { graphqlClient } from '$lib/graphql/client';
import type { Event } from '$lib/graphql/types';

export interface HomePageData {
  events: Event[];
  error: string | null;
}

export async function load(): Promise<HomePageData> {
  try {
    const result = await graphqlClient
      .query<{ events: Event[] }>(
        `
        query PublicEvents {
          events(status: "published", visibility: "public", limit: 24) {
            id
            name
            slug
            description
            event_type
            start_date
            end_date
            venue_city
            is_online
            cover_image_url
            max_tickets_per_order
          }
        }
        `,
        {}
      )
      .toPromise();

    if (result.error) {
      return { events: [], error: result.error.message };
    }

    return { events: result.data?.events ?? [], error: null };
  } catch {
    return { events: [], error: null };
  }
}
