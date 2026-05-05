import { createClient, cacheExchange, fetchExchange } from '@urql/svelte';
import { PUBLIC_GRAPHQL_URL } from '$env/static/public';
import { browser } from '$app/environment';

export const graphqlClient = createClient({
	url: PUBLIC_GRAPHQL_URL || 'http://localhost:8000/graphql',
	fetchOptions: (): RequestInit => {
		const headers: Record<string, string> = {};
		if (browser) {
			const token = localStorage.getItem('access_token');
			if (token) {
				headers['Authorization'] = `Bearer ${token}`;
			}
		}
		return { headers };
	},
	exchanges: [cacheExchange, fetchExchange]
});
