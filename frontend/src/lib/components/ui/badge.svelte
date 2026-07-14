<script lang="ts">
	import { cn } from '$lib/utils';

	type Variant = 'default' | 'primary' | 'secondary' | 'success' | 'warning' | 'error' | 'outline';

	interface Props {
		variant?: Variant;
		class?: string;
		children?: import('svelte').Snippet;
	}

	let { variant = 'default', class: className, children }: Props = $props();

	const variants: Record<Variant, string> = {
		default: 'bg-surface-container-high text-on-surface-variant',
		primary: 'bg-primary-fixed text-on-primary-fixed-variant',
		secondary: 'bg-secondary-fixed text-on-secondary-fixed-variant',
		success: 'bg-green-100 text-green-800',
		warning: 'bg-amber-100 text-amber-800',
		error: 'bg-error-container text-on-error-container',
		outline: 'border border-outline-variant text-on-surface-variant'
	};
</script>

<span
	class={cn(
		'inline-flex items-center rounded-full px-2.5 py-0.5 text-label-sm font-medium',
		variants[variant],
		className
	)}
>
	{@render children?.()}
</span>