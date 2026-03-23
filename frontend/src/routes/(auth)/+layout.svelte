<script lang="ts">
	import { page } from '$app/stores';
	import { goto } from '$app/navigation';
	import { isAuthenticated } from '$lib/stores/auth';

	let { children }: { children?: import('svelte').Snippet } = $props();

	$effect(() => {
		if ($isAuthenticated) {
			goto('/dashboard');
		}
	});
</script>

{@render children?.()}
