<script lang="ts">
	import { ambientAuth } from '$lib/ambient-auth.svelte';
	import Button from '$lib/components/ui/button.svelte';
	import Input from '$lib/components/ui/input.svelte';
	import Label from '$lib/components/ui/label.svelte';

	let email = $state('');
	let password = $state('');

	async function handleSubmit(event: Event) {
		event.preventDefault();
		await ambientAuth.login(email, password);
	}
</script>

<form onsubmit={handleSubmit} class="space-y-4">
	{#if ambientAuth.overlayError}
		<div class="rounded-lg border border-error-container/50 bg-error-container/10 p-3">
			<p class="text-body-md text-error">{ambientAuth.overlayError}</p>
		</div>
	{/if}
	<div class="space-y-1.5">
		<Label for="slide-email">Email</Label>
		<Input
			id="slide-email"
			type="email"
			placeholder="you@example.com"
			bind:value={email}
			required
		/>
	</div>
	<div class="space-y-1.5">
		<Label for="slide-password">Password</Label>
		<Input
			id="slide-password"
			type="password"
			placeholder="Enter your password"
			bind:value={password}
			required
		/>
	</div>
	<Button type="submit" variant="primary" size="lg" class="w-full" isLoading={ambientAuth.isSubmitting}>
		Sign in
	</Button>
</form>
