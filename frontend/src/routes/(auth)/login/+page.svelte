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
	let error = $state<string | null>(null);
	let isLoading = $state(false);

	async function handleSubmit(event: Event) {
		event.preventDefault();
		error = null;
		isLoading = true;

		try {
			await ambientAuth.login(email, password);
			goto('/dashboard');
		} catch (err) {
			error = err instanceof Error ? err.message : 'Login failed. Please try again.';
		} finally {
			isLoading = false;
		}
	}
</script>

<div class="flex min-h-[calc(100vh-4rem)] items-center justify-center p-6">
	<div class="w-full max-w-md animate-fade-in">
		<div class="text-center mb-8">
			<div class="mx-auto flex h-12 w-12 items-center justify-center rounded-2xl bg-primary text-on-primary">
				<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M15 3h4a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2h-4"/><polyline points="10 17 15 12 10 7"/><line x1="15" y1="12" x2="3" y2="12"/></svg>
			</div>
			<h1 class="mt-4 text-headline-xl font-bold text-fg">Welcome back</h1>
			<p class="mt-2 text-body-lg text-on-surface-variant">Sign in to your OpenMeet account</p>
		</div>

		<Card>
			<CardHeader>
				<CardTitle>Sign in</CardTitle>
				<CardDescription>Enter your email and password to continue</CardDescription>
			</CardHeader>
			<CardContent>
				<form onsubmit={handleSubmit} class="space-y-4">
					{#if error}
						<div class="rounded-lg border border-error-container/50 bg-error-container/10 p-3">
							<p class="text-body-md text-error">{error}</p>
						</div>
					{/if}
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
							placeholder="Enter your password"
							bind:value={password}
							required
						/>
					</div>
					<Button type="submit" variant="primary" size="lg" class="w-full" isLoading={isLoading}>
						Sign in
					</Button>
				</form>
				<div class="mt-6 text-center text-body-md text-on-surface-variant">
					Don't have an account?
					<a href="/register" class="ml-1 font-semibold text-primary hover:text-primary-container transition-colors">
						Sign up
					</a>
				</div>
			</CardContent>
		</Card>
	</div>
</div>
