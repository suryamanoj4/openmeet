<script lang="ts">
	import { goto } from '$app/navigation';
	import { ambientAuth } from '$lib/ambient-auth.svelte';
	import Button from '$lib/components/ui/button.svelte';
	import Input from '$lib/components/ui/input.svelte';
	import Label from '$lib/components/ui/label.svelte';
	import Card from '$lib/components/ui/card.svelte';
	import CardHeader from '$lib/components/ui/card-header.svelte';
	import CardTitle from '$lib/components/ui/card-title.svelte';
	import CardDescription from '$lib/components/ui/card-description.svelte';
	import CardContent from '$lib/components/ui/card-content.svelte';

	let email = $state('');
	let password = $state('');
	let confirmPassword = $state('');
	let firstName = $state('');
	let lastName = $state('');
	let error = $state<string | null>(null);
	let validationError = $state<string | null>(null);
	let isLoading = $state(false);

	async function handleSubmit(event: Event) {
		event.preventDefault();
		error = null;
		validationError = null;

		if (password !== confirmPassword) {
			validationError = 'Passwords do not match';
			return;
		}

		if (password.length < 8) {
			validationError = 'Password must be at least 8 characters';
			return;
		}

		isLoading = true;

		try {
			await ambientAuth.register({ email, password, first_name: firstName, last_name: lastName });
			goto('/dashboard');
		} catch (err) {
			error = err instanceof Error ? err.message : 'Registration failed. Please try again.';
		} finally {
			isLoading = false;
		}
	}
</script>

<div class="flex min-h-[calc(100vh-4rem)] items-center justify-center p-6">
	<div class="w-full max-w-md animate-fade-in">
		<div class="text-center mb-8">
			<div class="mx-auto flex h-12 w-12 items-center justify-center rounded-2xl bg-primary text-on-primary">
				<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/></svg>
			</div>
			<h1 class="mt-4 text-headline-xl font-bold text-fg">Create your account</h1>
			<p class="mt-2 text-body-lg text-on-surface-variant">Join OpenMeet and start creating events</p>
		</div>

		<Card>
			<CardHeader>
				<CardTitle>Sign up</CardTitle>
				<CardDescription>Fill in your details to get started</CardDescription>
			</CardHeader>
			<CardContent>
				<form onsubmit={handleSubmit} class="space-y-4">
					{#if validationError}
						<div class="rounded-lg border border-error-container/50 bg-error-container/10 p-3">
							<p class="text-body-md text-error">{validationError}</p>
						</div>
					{/if}
					{#if error}
						<div class="rounded-lg border border-error-container/50 bg-error-container/10 p-3">
							<p class="text-body-md text-error">{error}</p>
						</div>
					{/if}
					<div class="grid grid-cols-2 gap-4">
						<div class="space-y-1.5">
							<Label for="firstName">First name</Label>
							<Input
								id="firstName"
								type="text"
								placeholder="John"
								bind:value={firstName}
								required
							/>
						</div>
						<div class="space-y-1.5">
							<Label for="lastName">Last name</Label>
							<Input
								id="lastName"
								type="text"
								placeholder="Doe"
								bind:value={lastName}
								required
							/>
						</div>
					</div>
					<div class="space-y-1.5">
						<Label for="email">Email</Label>
						<Input
							id="email"
							type="email"
							placeholder="you@example.com"
							bind:value={email}
							required
						/>
					</div>
					<div class="space-y-1.5">
						<Label for="password">Password</Label>
						<Input
							id="password"
							type="password"
							placeholder="Create a password"
							bind:value={password}
							required
						/>
					</div>
					<div class="space-y-1.5">
						<Label for="confirmPassword">Confirm password</Label>
						<Input
							id="confirmPassword"
							type="password"
							placeholder="Confirm your password"
							bind:value={confirmPassword}
							required
						/>
					</div>
					<Button type="submit" variant="primary" size="lg" class="w-full" isLoading={isLoading}>
						Create account
					</Button>
				</form>
				<div class="mt-6 text-center text-body-md text-on-surface-variant">
					Already have an account?
					<a href="/login" class="ml-1 font-semibold text-primary hover:text-primary-container transition-colors">
						Sign in
					</a>
				</div>
			</CardContent>
		</Card>
	</div>
</div>
