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
		else await goto(`/event/${result.data.event.id}/${result.data.event.slug}`, { replaceState: true });
	});
</script>

<div class="mx-auto max-w-3xl px-6 py-20 text-center">
	{#if error}
		<p class="text-body-lg text-error">{error}</p>
	{:else}
		<div class="mx-auto h-12 w-12 animate-spin rounded-full border-4 border-primary/20 border-t-primary"></div>
		<p class="mt-4 text-body-md text-on-surface-variant">Opening the published event…</p>
	{/if}
</div>
