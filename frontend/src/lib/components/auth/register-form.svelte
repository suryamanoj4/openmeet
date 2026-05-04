<script lang="ts">
	import { ambientAuth } from '$lib/ambient-auth.svelte';
	import Button from '$lib/components/ui/button.svelte';
	import Input from '$lib/components/ui/input.svelte';
	import Label from '$lib/components/ui/label.svelte';

	let firstName = $state('');
	let lastName = $state('');
	let email = $state('');
	let password = $state('');
	let confirmPassword = $state('');
	let validationError = $state<string | null>(null);

	async function handleSubmit(event: Event) {
		event.preventDefault();
		validationError = null;

		if (password !== confirmPassword) {
			validationError = 'Passwords do not match';
			return;
		}

		if (password.length < 8) {
			validationError = 'Password must be at least 8 characters';
			return;
		}

		await ambientAuth.register({ email, password, first_name: firstName, last_name: lastName });
	}
</script>

<form onsubmit={handleSubmit} class="space-y-4">
	{#if validationError}
		<div class="rounded-lg border border-error-container/50 bg-error-container/10 p-3">
			<p class="text-body-md text-error">{validationError}</p>
		</div>
	{/if}
	{#if ambientAuth.overlayError}
		<div class="rounded-lg border border-error-container/50 bg-error-container/10 p-3">
			<p class="text-body-md text-error">{ambientAuth.overlayError}</p>
		</div>
	{/if}
	<div class="grid grid-cols-2 gap-4">
		<div class="space-y-1.5">
			<Label for="slide-firstName">First name</Label>
			<Input
				id="slide-firstName"
				type="text"
				placeholder="John"
				bind:value={firstName}
				required
			/>
		</div>
		<div class="space-y-1.5">
			<Label for="slide-lastName">Last name</Label>
			<Input
				id="slide-lastName"
				type="text"
				placeholder="Doe"
				bind:value={lastName}
				required
			/>
		</div>
	</div>
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
			placeholder="Create a password"
			bind:value={password}
			required
		/>
	</div>
	<div class="space-y-1.5">
		<Label for="slide-confirmPassword">Confirm password</Label>
		<Input
			id="slide-confirmPassword"
			type="password"
			placeholder="Confirm your password"
			bind:value={confirmPassword}
			required
		/>
	</div>
	<Button type="submit" variant="primary" size="lg" class="w-full" isLoading={ambientAuth.isSubmitting}>
		Create account
	</Button>
</form>
