<script lang="ts">
	import { cn } from '$lib/utils';
	import type { HTMLLabelAttributes } from 'svelte/elements';

	interface Props extends HTMLLabelAttributes {}

	let { class: className, children, ...restProps }: Props = $props();
</script>

<label
	class={cn(
		'text-label-md text-fg',
		className
	)}
	{...restProps}
>
	{@render children?.()}
</label>
