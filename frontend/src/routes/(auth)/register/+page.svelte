<script lang="ts">
	import { cn } from '$lib/utils';
	import { goto } from '$app/navigation';
	import { register } from '$lib/services/auth';
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
	let isLoading = $state(false);

	async function handleSubmit(event: Event) {
		event.preventDefault();
		error = null;

		// Validation
		if (password !== confirmPassword) {
			error = 'Passwords do not match';
			return;
		}

		if (password.length < 8) {
			error = 'Password must be at least 8 characters';
			return;
		}

		isLoading = true;

		try {
			await register(email, password, firstName, lastName);
			// Redirect to dashboard after successful registration
			goto('/dashboard');
		} catch (err) {
			error = err instanceof Error ? err.message : 'Registration failed. Please try again.';
		} finally {
			isLoading = false;
		}
	}
</script>

<div class="flex min-h-screen items-center justify-center p-4">
	<Card class="w-full max-w-md">
		<CardHeader class="space-y-1">
			<CardTitle class="text-2xl font-bold">Create an account</CardTitle>
			<CardDescription>
				Enter your details to get started with OpenMeets
			</CardDescription>
		</CardHeader>
		<CardContent>
			<form onsubmit={handleSubmit} class="space-y-4">
				{#if error}
					<div class="rounded-md bg-destructive/15 p-3 text-sm text-destructive">
						{error}
					</div>
				{/if}
				<div class="grid grid-cols-2 gap-4">
					<div class="space-y-2">
						<Label for="firstName">First name</Label>
						<Input
							id="firstName"
							type="text"
							placeholder="John"
							value={firstName}
							oninput={(e) => (firstName = e.currentTarget.value)}
							required
						/>
					</div>
					<div class="space-y-2">
						<Label for="lastName">Last name</Label>
						<Input
							id="lastName"
							type="text"
							placeholder="Doe"
							value={lastName}
							oninput={(e) => (lastName = e.currentTarget.value)}
							required
						/>
					</div>
				</div>
				<div class="space-y-2">
					<Label for="email">Email</Label>
					<Input
						id="email"
						type="email"
						placeholder="you@example.com"
						value={email}
						oninput={(e) => (email = e.currentTarget.value)}
						required
					/>
				</div>
				<div class="space-y-2">
					<Label for="password">Password</Label>
					<Input
						id="password"
						type="password"
						placeholder="••••••••"
						value={password}
						oninput={(e) => (password = e.currentTarget.value)}
						required
					/>
				</div>
				<div class="space-y-2">
					<Label for="confirmPassword">Confirm password</Label>
					<Input
						id="confirmPassword"
						type="password"
						placeholder="••••••••"
						value={confirmPassword}
						oninput={(e) => (confirmPassword = e.currentTarget.value)}
						required
					/>
				</div>
				<Button type="submit" class="w-full" isLoading={isLoading}>
					Create account
				</Button>
			</form>
			<div class="mt-4 text-center text-sm">
				Already have an account?
				<a href="/login" class="ml-1 text-primary underline-offset-4 hover:underline">
					Sign in
				</a>
			</div>
		</CardContent>
	</Card>
</div>
