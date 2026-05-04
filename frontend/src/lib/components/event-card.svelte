<script lang="ts">
	import { ambientAuth } from '$lib/ambient-auth.svelte';
	import Button from '$lib/components/ui/button.svelte';
	import { Calendar, MapPin } from 'lucide-svelte';
	import type { Event } from '$lib/graphql/types';

	interface Props {
		event: Event;
		onRegister?: (eventId: string) => void;
	}

	let { event, onRegister }: Props = $props();

	function formatDate(dateStr: string): string {
		const d = new Date(dateStr);
		return d.toLocaleDateString('en-US', {
			weekday: 'short',
			month: 'short',
			day: 'numeric',
			hour: 'numeric',
			minute: '2-digit'
		});
	}

	function handleAction() {
		if (ambientAuth.isAuthenticated) {
			onRegister?.(event.id);
		} else {
			ambientAuth.requireAuth({
				kind: 'register-ticket',
				label: 'Get tickets',
				execute: () => onRegister?.(event.id)
			});
		}
	}
</script>

<div class="bg-surface-container-lowest rounded-xl overflow-hidden shadow-card hover:shadow-md transition-all duration-200 group border border-outline-variant">
	<div class="relative h-48 overflow-hidden bg-surface-container">
		{#if event.cover_image_url}
			<img
				src={event.cover_image_url}
				alt={event.name}
				class="w-full h-full object-cover transition-transform duration-300 group-hover:scale-105"
			/>
		{:else}
			<div class="w-full h-full bg-gradient-to-br from-primary-fixed-dim/20 to-surface-container-highest flex items-center justify-center">
				<Calendar size={32} class="text-on-surface-variant/30" />
			</div>
		{/if}
		<div class="absolute top-3 left-3 bg-surface-container-lowest/90 backdrop-blur px-3 py-1 rounded-full shadow-sm">
			<span class="text-[10px] font-bold text-fg uppercase tracking-wider">{event.event_type || 'Event'}</span>
		</div>
	</div>

	<div class="p-5">
		<div class="flex items-start justify-between mb-3">
			<h3 class="text-headline-md font-semibold text-fg line-clamp-1 group-hover:text-primary transition-colors">
				{event.name}
			</h3>
			<span class="text-label-md font-bold text-primary shrink-0 ml-2">Free</span>
		</div>

		<div class="space-y-2 mb-5">
			<div class="flex items-center gap-2 text-body-md text-on-surface-variant">
				<Calendar size={14} class="shrink-0" />
				<span>{formatDate(event.start_date)}</span>
			</div>
			<div class="flex items-center gap-2 text-body-md text-on-surface-variant">
				<MapPin size={14} class="shrink-0" />
				<span>{event.venue_city || (event.is_online ? 'Online' : 'TBD')}</span>
			</div>
		</div>

		<Button
			variant="outline"
			size="md"
			class="w-full border-primary-fixed text-primary font-bold hover:bg-primary hover:text-on-primary transition-all"
			onclick={handleAction}
		>
			View Details
		</Button>
	</div>
</div>
