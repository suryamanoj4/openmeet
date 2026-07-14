<script lang="ts">
	import { cn } from '$lib/utils';
	import { Check, ChevronDown } from 'lucide-svelte';
	import type { HTMLSelectAttributes } from 'svelte/elements';

	interface Option {
		value: string;
		label: string;
	}

	interface Props {
		options: Option[];
		label?: string;
		error?: string;
		placeholder?: string;
		class?: string;
		value?: string;
		onchange?: (value: string) => void;
		disabled?: boolean;
	}

	let {
		options,
		label,
		error,
		placeholder = 'Select...',
		class: className,
		value = $bindable(''),
		onchange,
		disabled = false
	}: Props = $props();

	let open = $state(false);
	let containerEl = $state<HTMLElement>();

	function select(opt: Option) {
		value = opt.value;
		open = false;
		onchange?.(opt.value);
	}

	function handleClickOutside(e: MouseEvent) {
		if (containerEl && !containerEl.contains(e.target as Node)) {
			open = false;
		}
	}

	$effect(() => {
		if (open) {
			document.addEventListener('click', handleClickOutside);
			return () => document.removeEventListener('click', handleClickOutside);
		}
	});

	const selectedLabel = $derived(options.find((o) => o.value === value)?.label ?? placeholder);
</script>

<div class="w-full space-y-1.5" bind:this={containerEl}>
	{#if label}
		<label class="text-label-md text-fg">{label}</label>
	{/if}
	<button
		type="button"
		class={cn(
			'flex h-10 w-full items-center justify-between rounded-lg border bg-surface-container-lowest px-3 py-2 text-body-md transition-all duration-150',
			error ? 'border-error focus-visible:ring-error' : 'border-input focus-visible:ring-ring',
			disabled && 'cursor-not-allowed opacity-50',
			className
		)}
		onclick={() => (open = !open)}
		{disabled}
	>
		<span class={selectedLabel === placeholder ? 'text-on-surface-variant/60' : 'text-fg'}>
			{selectedLabel}
		</span>
		<ChevronDown size={16} class="text-on-surface-variant transition-transform {open ? 'rotate-180' : ''}" />
	</button>
	{#if error}
		<p class="text-body-md text-error">{error}</p>
	{/if}
	{#if open}
		<div
			class="absolute z-50 mt-1 w-[var(--trigger-width)] rounded-lg border border-outline-variant bg-surface-container-lowest shadow-lg max-h-60 overflow-auto"
			style="--trigger-width: {containerEl?.offsetWidth ?? 0}px"
		>
			{#each options as opt}
				<button
					type="button"
					class="flex w-full items-center justify-between px-3 py-2 text-body-md hover:bg-surface-container-low transition-colors {opt.value === value ? 'bg-primary-fixed/30 text-fg' : 'text-on-surface-variant'}"
					onclick={() => select(opt)}
				>
					{opt.label}
					{#if opt.value === value}
						<Check size={14} class="text-primary" />
					{/if}
				</button>
			{/each}
		</div>
	{/if}
</div>