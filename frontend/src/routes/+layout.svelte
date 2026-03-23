<script lang="ts">
	import '../app.css';
	import { onMount } from 'svelte';
	import { authStore, isAuthenticated } from '$lib/stores/auth';
	import { getMe } from '$lib/services/auth';
	import type { User } from '$lib/graphql/types';

	let { children }: { children?: import('svelte').Snippet } = $props();

	onMount(async () => {
		// Load tokens from storage
		const { accessToken } = authStore.loadFromStorage();

		// If we have tokens, fetch the current user
		if (accessToken) {
			try {
				const user = await getMe();
				if (user) {
					authStore.setUser(user as User);
				} else {
					// Token is invalid, clear auth state
					authStore.logout();
				}
			} catch (error) {
				console.error('Failed to fetch user:', error);
				authStore.logout();
			}
		} else {
			authStore.setLoading(false);
		}
	});
</script>

<div class="min-h-screen bg-background">
	{@render children?.()}
</div>
