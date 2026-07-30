import { createClient, cacheExchange, fetchExchange } from '@urql/svelte';
import { env } from '$env/dynamic/public';
import { browser } from '$app/environment';

export const graphqlClient = createClient({
	url: env.PUBLIC_GRAPHQL_URL || '/graphql',
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
