import { createClient, cacheExchange, fetchExchange } from '@urql/svelte';
import { PUBLIC_GRAPHQL_URL } from '$env/static/public';

export const graphqlClient = createClient({
	url: PUBLIC_GRAPHQL_URL || 'http://localhost:8000/graphql',
	exchanges: [cacheExchange, fetchExchange]
});
