<script lang="ts">
	import { goto } from '$app/navigation';
	import { createOrganization } from '$lib/services/organizations';
	import Button from '$lib/components/ui/button.svelte';
	import Input from '$lib/components/ui/input.svelte';
	import Label from '$lib/components/ui/label.svelte';
	import Card from '$lib/components/ui/card.svelte';
	import CardHeader from '$lib/components/ui/card-header.svelte';
	import CardTitle from '$lib/components/ui/card-title.svelte';
	import CardContent from '$lib/components/ui/card-content.svelte';
	import { ArrowLeft } from 'lucide-svelte';

	let name = $state('');
	let slug = $state('');
	let description = $state('');
	let error = $state<string | null>(null);
	let saving = $state(false);

	async function handleSubmit(e: Event) {
		e.preventDefault();
		error = null;
		saving = true;
		try {
			const org = await createOrganization({ name, slug, description });
			if (org) goto(`/organizations/${org.id}`);
			else error = 'Failed to create organization';
		} catch (err) {
			error = err instanceof Error ? err.message : 'Failed to create';
		} finally {
			saving = false;
		}
	}
</script>

<div class="mx-auto max-w-2xl px-6 py-8">
	<button onclick={() => goto('/organizations')} class="flex items-center gap-2 text-body-md text-on-surface-variant hover:text-fg mb-6 transition-colors">
		<ArrowLeft size={18} />
		Back to organizations
	</button>

	<Card>
		<CardHeader>
			<CardTitle>Create Organization</CardTitle>
		</CardHeader>
		<CardContent>
			<form onsubmit={handleSubmit} class="space-y-5">
				{#if error}
					<div class="rounded-lg border border-error-container/50 bg-error-container/10 p-3">
						<p class="text-body-md text-error">{error}</p>
					</div>
				{/if}
				<div class="space-y-1.5">
					<Label for="name">Name</Label>
					<Input id="name" type="text" placeholder="My Organization" bind:value={name} required />
				</div>
				<div class="space-y-1.5">
					<Label for="slug">Slug</Label>
					<Input id="slug" type="text" placeholder="my-organization" bind:value={slug} required />
				</div>
				<div class="space-y-1.5">
					<Label for="desc">Description</Label>
					<textarea id="desc" bind:value={description} class="flex min-h-[100px] w-full rounded-lg border border-input bg-surface-container-lowest px-3 py-2 text-body-md text-fg placeholder:text-on-surface-variant/60 ring-offset-surface-container-lowest transition-all focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2" placeholder="Description of your organization"></textarea>
				</div>
				<div class="flex gap-3 pt-2">
					<Button type="submit" variant="primary" size="lg" isLoading={saving}>Create</Button>
					<Button type="button" variant="outline" size="lg" onclick={() => goto('/organizations')}>Cancel</Button>
				</div>
			</form>
		</CardContent>
	</Card>
</div>
