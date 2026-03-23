<script lang="ts">
	import { cn } from '$lib/utils';
	import type { HTMLInputAttributes } from 'svelte/elements';

	interface Props extends HTMLInputAttributes {
		label?: string;
		error?: string;
		value?: string;
	}

	let { class: className, label, error, id, value = $bindable(), ...restProps }: Props = $props();
</script>

<div class="w-full">
	{#if label}
		<label
			for={id}
			class="text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70"
		>
			{label}
		</label>
	{/if}
	<input
		id={id}
		class={cn(
			'flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background file:border-0 file:bg-transparent file:text-sm file:font-medium placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50',
			className
		)}
		value={value}
		oninput={(e) => (value = e.currentTarget.value)}
		{...restProps}
	/>
	{#if error}
		<p class="mt-1 text-sm text-destructive">{error}</p>
	{/if}
</div>
