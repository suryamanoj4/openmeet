<script lang="ts">
	import { onMount } from 'svelte';
	import { goto } from '$app/navigation';
	import { Lock, ArrowLeft, CheckCircle } from 'lucide-svelte';
	import Button from '$lib/components/ui/button.svelte';
	import Input from '$lib/components/ui/input.svelte';
	import { confirmPasswordReset } from '$lib/services/auth';

	let token = $state('');
	let password = $state('');
	let confirmPassword = $state('');
	let error = $state('');
	let loading = $state(false);
	let success = $state(false);
	let invalidToken = $state(false);

	onMount(() => {
		const params = new URLSearchParams(window.location.search);
		const t = params.get('token');
		if (t) { token = t; } else { invalidToken = true; }
	});

	async function handleSubmit(e: Event) {
		e.preventDefault();
		error = '';
		if (password.length < 6) { error = 'Password must be at least 6 characters'; return; }
		if (password !== confirmPassword) { error = 'Passwords do not match'; return; }
		loading = true;
		try {
			const ok = await confirmPasswordReset(token, password);
			if (ok) { success = true; } else { error = 'Failed to reset password. The link may have expired.'; }
		} catch (err) {
			error = err instanceof Error ? err.message : 'Something went wrong';
		}
		loading = false;
	}
</script>

<div class="flex min-h-screen items-center justify-center px-4">
	<div class="w-full max-w-md">
		{#if invalidToken}
			<div class="text-center">
				<h1 class="text-headline-xl font-bold text-fg mb-3">Invalid Link</h1>
				<p class="text-body-md text-on-surface-variant mb-4">This password reset link is invalid or has expired.</p>
				<Button variant="primary" onclick={() => goto('/forgot-password')}>Request a new link</Button>
			</div>
		{:else if success}
			<div class="text-center">
				<div class="mx-auto flex h-16 w-16 items-center justify-center rounded-full bg-green-100 mb-6">
					<CheckCircle size={32} class="text-green-600" />
				</div>
				<h1 class="text-headline-xl font-bold text-fg mb-3">Password Reset</h1>
				<p class="text-body-md text-on-surface-variant mb-6">Your password has been reset successfully.</p>
				<Button variant="primary" size="lg" onclick={() => goto('/login')}>Log In</Button>
			</div>
		{:else}
			<button onclick={() => goto('/forgot-password')} class="flex items-center gap-2 text-body-md text-on-surface-variant hover:text-fg mb-8 transition-colors">
				<ArrowLeft size={18} /> Back
			</button>
			<div class="mb-8">
				<div class="flex h-12 w-12 items-center justify-center rounded-xl bg-primary-fixed text-primary mb-4">
					<Lock size={24} />
				</div>
				<h1 class="text-headline-xl font-bold text-fg">Reset Password</h1>
				<p class="text-body-md text-on-surface-variant mt-2">Choose a new password for your account.</p>
			</div>

			<form onsubmit={handleSubmit} class="space-y-4">
				<Input id="password" type="password" label="New Password" placeholder="Min. 6 characters" bind:value={password} required />
				<Input id="confirm" type="password" label="Confirm Password" bind:value={confirmPassword} error={error} required />
				<Button type="submit" variant="primary" size="lg" class="w-full" isLoading={loading}>
					Reset Password
				</Button>
			</form>
		{/if}
	</div>
</div>