<script lang="ts">
	import { cn } from '$lib/utils';
	import type { HTMLInputAttributes } from 'svelte/elements';

	interface Props extends HTMLInputAttributes {
		label?: string;
		error?: string;
	}

	let { class: className, label, error, id, value = $bindable(), ...restProps }: Props = $props();
</script>

<div class="w-full space-y-1.5">
	{#if label}
		<label for={id} class="text-label-md text-fg">
			{label}
		</label>
	{/if}
	<input
		{id}
		class={cn(
			'flex h-10 w-full rounded-lg border border-input bg-surface-container-lowest px-3 py-2 text-body-md text-fg placeholder:text-on-surface-variant/60 ring-offset-surface-container-lowest transition-all duration-150 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50',
			error && 'border-error focus-visible:ring-error',
			className
		)}
		bind:value
		{...restProps}
	/>
	{#if error}
		<p class="text-body-md text-error">{error}</p>
	{/if}
</div>
