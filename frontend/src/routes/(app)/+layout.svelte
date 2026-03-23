<script lang="ts">
	import { goto } from '$app/navigation';
	import { authStore, isAuthenticated } from '$lib/stores/auth';

	let { children }: { children?: import('svelte').Snippet } = $props();

	$effect(() => {
		if (!$isAuthenticated && !$authStore.isLoading) {
			goto('/login');
		}
	});
</script>

{@render children?.()}
