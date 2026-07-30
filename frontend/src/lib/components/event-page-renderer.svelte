<script lang="ts">
	import type { EventPageBlock } from '$lib/event-page';
	import { safeLink, videoEmbedUrl } from '$lib/event-page';

	let { blocks }: { blocks: EventPageBlock[] } = $props();
</script>

<div class="space-y-8">
	{#each blocks.filter((block) => block.visible) as block (block.id)}
		{@const props = block.props}
		{#if block.type === 'hero'}
			<section class="rounded-2xl px-8 py-16 text-center" style={`background-color: ${String(props.bgColor || '#1a1a2e')}`}>
				<h2 class="text-4xl font-bold text-white">{String(props.headline || '')}</h2>
				<p class="mt-4 text-xl text-white/80">{String(props.subheadline || '')}</p>
				{#if props.ctaText}<a class="mt-6 inline-flex rounded-xl bg-white px-7 py-3 font-semibold text-black" href={safeLink(props.ctaLink)}>{String(props.ctaText)}</a>{/if}
			</section>
		{:else if block.type === 'text'}
			<p class="whitespace-pre-line text-body-lg text-fg">{String(props.content || '')}</p>
		{:else if block.type === 'image' && props.url}
			<figure><img class="max-h-[34rem] w-full rounded-2xl object-cover" src={safeLink(props.url)} alt={String(props.alt || '')} />{#if props.caption}<figcaption class="mt-2 text-center text-body-md text-on-surface-variant">{String(props.caption)}</figcaption>{/if}</figure>
		{:else if block.type === 'about'}
			<section><h2 class="text-headline-lg font-bold text-fg">{String(props.title || 'About')}</h2><p class="mt-3 whitespace-pre-line text-body-md text-on-surface-variant">{String(props.content || '')}</p></section>
		{:else if block.type === 'schedule'}
			<section><h2 class="mb-4 text-headline-lg font-bold text-fg">{String(props.title || 'Schedule')}</h2><div class="space-y-3">{#each (Array.isArray(props.items) ? props.items : []) as item}<div class="flex gap-4 rounded-xl border border-outline-variant p-4"><strong class="min-w-20 text-primary">{String(item.time || '')}</strong><div><h3 class="font-semibold text-fg">{String(item.title || '')}</h3><p class="text-on-surface-variant">{String(item.description || '')}</p></div></div>{/each}</div></section>
		{:else if block.type === 'speakers'}
			<section><h2 class="mb-4 text-headline-lg font-bold text-fg">{String(props.title || 'Speakers')}</h2><div class="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">{#each (Array.isArray(props.items) ? props.items : []) as item}<article class="rounded-xl border border-outline-variant p-5 text-center">{#if item.photo}<img class="mx-auto mb-3 h-20 w-20 rounded-full object-cover" src={safeLink(item.photo)} alt={String(item.name || '')} />{/if}<h3 class="font-semibold">{String(item.name || '')}</h3><p class="text-primary">{String(item.role || '')}</p><p class="mt-2 text-on-surface-variant">{String(item.bio || '')}</p></article>{/each}</div></section>
		{:else if block.type === 'venue'}
			<section><h2 class="text-headline-lg font-bold text-fg">{String(props.title || 'Venue')}</h2><p class="mt-3 text-fg">{String(props.address || '')}</p><p class="text-on-surface-variant">{String(props.city || '')}</p></section>
		{:else if block.type === 'faqs'}
			<section><h2 class="mb-4 text-headline-lg font-bold text-fg">{String(props.title || 'Frequently Asked Questions')}</h2><div class="space-y-3">{#each (Array.isArray(props.items) ? props.items : []) as item}<details class="rounded-xl border border-outline-variant p-4"><summary class="cursor-pointer font-semibold">{String(item.question || '')}</summary><p class="mt-3 text-on-surface-variant">{String(item.answer || '')}</p></details>{/each}</div></section>
		{:else if block.type === 'cta'}
			<section class="rounded-2xl bg-primary-fixed/30 px-8 py-14 text-center"><h2 class="text-headline-lg font-bold">{String(props.headline || '')}</h2><a class="mt-5 inline-flex rounded-xl bg-primary px-7 py-3 font-semibold text-on-primary" href={safeLink(props.buttonLink)}>{String(props.buttonText || 'Register')}</a></section>
		{:else if block.type === 'video'}
			{@const embedUrl = videoEmbedUrl(props.url)}
			{#if embedUrl}<section><h2 class="mb-4 text-headline-lg font-bold">{String(props.title || '')}</h2><iframe class="aspect-video w-full rounded-2xl" src={embedUrl} title={String(props.title || 'Event video')} allowfullscreen></iframe></section>{/if}
		{:else if block.type === 'divider'}
			<hr class="border-outline-variant" />
		{/if}
	{/each}
</div>
