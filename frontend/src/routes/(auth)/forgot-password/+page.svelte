<script lang="ts">
	import { goto } from '$app/navigation';
	import { Mail, ArrowLeft, CheckCircle } from 'lucide-svelte';
	import Button from '$lib/components/ui/button.svelte';
	import Input from '$lib/components/ui/input.svelte';
	import { requestPasswordReset } from '$lib/services/auth';

	let email = $state('');
	let error = $state('');
	let loading = $state(false);
	let sent = $state(false);

	async function handleSubmit(e: Event) {
		e.preventDefault();
		if (!email) { error = 'Email is required'; return; }
		error = '';
		loading = true;
		try {
			await requestPasswordReset(email);
			sent = true;
		} catch (err) {
			error = err instanceof Error ? err.message : 'Something went wrong';
		}
		loading = false;
	}
</script>

<div class="flex min-h-screen items-center justify-center px-4">
	<div class="w-full max-w-md">
		<button onclick={() => goto('/login')} class="flex items-center gap-2 text-body-md text-on-surface-variant hover:text-fg mb-8 transition-colors">
			<ArrowLeft size={18} /> Back to login
		</button>

		{#if sent}
			<div class="text-center">
				<div class="mx-auto flex h-16 w-16 items-center justify-center rounded-full bg-green-100 mb-6">
					<CheckCircle size={32} class="text-green-600" />
				</div>
				<h1 class="text-headline-xl font-bold text-fg mb-3">Check Your Email</h1>
				<p class="text-body-md text-on-surface-variant mb-6">
					We sent a password reset link to <span class="text-fg font-medium">{email}</span>. Click the link to reset your password.
				</p>
				<p class="text-label-sm text-on-surface-variant/60">Didn't receive it? Check spam or <button class="text-primary underline" onclick={() => sent = false}>try again</button>.</p>
			</div>
		{:else}
			<div class="mb-8">
				<div class="flex h-12 w-12 items-center justify-center rounded-xl bg-primary-fixed text-primary mb-4">
					<Mail size={24} />
				</div>
				<h1 class="text-headline-xl font-bold text-fg">Forgot Password</h1>
				<p class="text-body-md text-on-surface-variant mt-2">Enter your email and we'll send you a reset link.</p>
			</div>

			<form onsubmit={handleSubmit} class="space-y-4">
				<Input id="email" type="email" label="Email" placeholder="you@example.com" bind:value={email} error={error} required />
				<Button type="submit" variant="primary" size="lg" class="w-full" isLoading={loading}>
					Send Reset Link
				</Button>
			</form>
		{/if}
	</div>
</div>