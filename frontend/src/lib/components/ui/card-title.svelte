<script lang="ts">
	import { cn } from '$lib/utils';

	interface Props {
		class?: string;
		children?: import('svelte').Snippet;
	}

	let { class: className, children }: Props = $props();
</script>

<h3 class={cn('text-headline-lg font-semibold tracking-tight text-fg', className)}>
	{@render children?.()}
</h3>
