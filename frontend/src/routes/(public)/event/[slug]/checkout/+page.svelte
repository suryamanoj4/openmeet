<script lang="ts">
	import { onMount } from 'svelte';
	import { goto } from '$app/navigation';
	import { page } from '$app/stores';
	import { graphqlClient } from '$lib/graphql/client';
	import { RESOLVE_PUBLIC_EVENT_SLUG } from '$lib/graphql/queries/events';

	let error = $state<string | null>(null);
	onMount(async () => {
		const result = await graphqlClient.query<{ event: { id: string; slug: string } | null }>(
			RESOLVE_PUBLIC_EVENT_SLUG,
			{ slug: $page.params.slug }
		).toPromise();
		if (result.error) error = result.error.message;
		else if (!result.data?.event) error = 'Published event not found or the link is ambiguous.';
		else await goto(`/event/${result.data.event.id}/${result.data.event.slug}/checkout`, { replaceState: true });
	});
</script>

<div class="mx-auto max-w-2xl px-6 py-20 text-center">
	{#if error}<p class="text-error">{error}</p>{:else}<p class="text-on-surface-variant">Opening secure checkout…</p>{/if}
</div>
