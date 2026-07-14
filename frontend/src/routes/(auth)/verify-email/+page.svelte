<script lang="ts">
	import { onMount } from 'svelte';
	import { goto } from '$app/navigation';
	import { Mail, CheckCircle, AlertCircle } from 'lucide-svelte';
	import Button from '$lib/components/ui/button.svelte';
	import Spinner from '$lib/components/ui/spinner.svelte';
	import { verifyEmail } from '$lib/services/auth';

	let loading = $state(true);
	let success = $state(false);
	let error = $state('');
	let invalidToken = $state(false);

	onMount(async () => {
		const params = new URLSearchParams(window.location.search);
		const token = params.get('token');
		if (!token) { invalidToken = true; loading = false; return; }
		try {
			const ok = await verifyEmail(token);
			if (ok) { success = true; } else { error = 'Verification failed. The link may have expired.'; }
		} catch (err) {
			error = err instanceof Error ? err.message : 'Email verification failed';
		}
		loading = false;
	});
</script>

<div class="flex min-h-screen items-center justify-center px-4">
	<div class="w-full max-w-md text-center">
		{#if loading}
			<Spinner size="lg" class="mx-auto" />
			<p class="text-body-md text-on-surface-variant mt-4">Verifying your email...</p>
		{:else if success}
			<div class="mx-auto flex h-16 w-16 items-center justify-center rounded-full bg-green-100 mb-6">
				<CheckCircle size={32} class="text-green-600" />
			</div>
			<h1 class="text-headline-xl font-bold text-fg mb-3">Email Verified</h1>
			<p class="text-body-md text-on-surface-variant mb-6">Your email has been verified. You can now use all features.</p>
			<Button variant="primary" size="lg" onclick={() => goto('/')}>Go to Dashboard</Button>
		{:else if invalidToken}
			<div class="mx-auto flex h-16 w-16 items-center justify-center rounded-full bg-amber-100 mb-6">
				<AlertCircle size={32} class="text-amber-600" />
			</div>
			<h1 class="text-headline-xl font-bold text-fg mb-3">Invalid Link</h1>
			<p class="text-body-md text-on-surface-variant mb-4">This verification link is invalid or missing.</p>
			<Button variant="primary" onclick={() => goto('/')}>Go Home</Button>
		{:else}
			<div class="mx-auto flex h-16 w-16 items-center justify-center rounded-full bg-red-100 mb-6">
				<AlertCircle size={32} class="text-red-600" />
			</div>
			<h1 class="text-headline-xl font-bold text-fg mb-3">Verification Failed</h1>
			<p class="text-body-md text-on-surface-variant mb-4">{error}</p>
			<Button variant="outline" onclick={() => goto('/')}>Go Home</Button>
		{/if}
	</div>
</div>