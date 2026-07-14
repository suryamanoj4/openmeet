<script lang="ts">
	import { cn } from '$lib/utils';
	import { X } from 'lucide-svelte';

	interface Props {
		class?: string;
		open?: boolean;
		onclose?: () => void;
		title?: string;
		description?: string;
		size?: 'sm' | 'md' | 'lg' | 'xl';
		children?: import('svelte').Snippet;
	}

	let {
		class: className,
		open = $bindable(false),
		onclose,
		title,
		description,
		size = 'md',
		children
	}: Props = $props();

	const sizes = {
		sm: 'max-w-sm',
		md: 'max-w-md',
		lg: 'max-w-lg',
		xl: 'max-w-xl'
	};

	function close() {
		open = false;
		onclose?.();
	}

	function handleKeydown(e: KeyboardEvent) {
		if (e.key === 'Escape') close();
	}
</script>

<svelte:window onkeydown={handleKeydown} />

{#if open}
	<!-- backdrop -->
	<button
		type="button"
		class="fixed inset-0 z-40 bg-black/50 backdrop-blur-sm animate-in fade-in"
		onclick={close}
		aria-label="Close dialog"
	></button>

	<!-- dialog -->
	<div
		role="dialog"
		aria-modal="true"
		class={cn(
			'fixed left-1/2 top-1/2 z-50 -translate-x-1/2 -translate-y-1/2 w-full rounded-2xl border border-outline-variant bg-surface-container-lowest p-6 shadow-2xl animate-in zoom-in-95',
			sizes[size],
			className
		)}
	>
		<!-- header -->
		<div class="flex items-start justify-between mb-4">
			<div>
				{#if title}
					<h2 class="text-headline-md font-semibold text-fg">{title}</h2>
				{/if}
				{#if description}
					<p class="text-body-md text-on-surface-variant mt-1">{description}</p>
				{/if}
			</div>
			<button
				type="button"
				class="rounded-lg p-1.5 text-on-surface-variant hover:bg-surface-container-low transition-colors"
				onclick={close}
				aria-label="Close"
			>
				<X size={18} />
			</button>
		</div>

		<!-- body -->
		<div>
			{@render children?.()}
		</div>
	</div>
{/if}