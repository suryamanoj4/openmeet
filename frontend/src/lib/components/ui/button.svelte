<script lang="ts">
	import { cn } from '$lib/utils';
	import type { HTMLButtonAttributes } from 'svelte/elements';

	type Variant = 'primary' | 'secondary' | 'outline' | 'ghost' | 'destructive' | 'link';
	type Size = 'sm' | 'md' | 'lg' | 'xl' | 'icon';

	interface Props extends HTMLButtonAttributes {
		variant?: Variant;
		size?: Size;
		isLoading?: boolean;
	}

	let {
		class: className,
		variant = 'primary',
		size = 'md',
		isLoading = false,
		disabled,
		children,
		...restProps
	}: Props = $props();

	const variants: Record<Variant, string> = {
		primary: 'bg-primary text-on-primary hover:bg-primary-container hover:text-on-primary-container shadow-sm',
		secondary: 'bg-secondary text-on-secondary hover:bg-secondary/80 shadow-sm',
		outline: 'border border-outline-variant bg-surface-container-lowest text-fg hover:bg-surface-container-low',
		ghost: 'text-fg hover:bg-surface-container-low',
		destructive: 'bg-error text-on-error hover:bg-error/90 shadow-sm',
		link: 'text-primary underline-offset-4 hover:underline'
	};

	const sizes: Record<Size, string> = {
		sm: 'h-8 px-3 text-label-sm rounded-md',
		md: 'h-10 px-4 text-label-md rounded-lg',
		lg: 'h-12 px-6 text-label-md rounded-lg',
		xl: 'h-14 px-8 text-label-md rounded-xl',
		icon: 'h-10 w-10 rounded-lg'
	};
</script>

<button
	class={cn(
		'inline-flex items-center justify-center whitespace-nowrap font-semibold transition-all duration-150 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50',
		variants[variant],
		sizes[size],
		className
	)}
	{disabled}
	{...restProps}
>
	{#if isLoading}
		<svg class="animate-spin -ml-1 mr-2 h-4 w-4" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
			<circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" />
			<path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
		</svg>
	{/if}
	{@render children?.()}
</button>
