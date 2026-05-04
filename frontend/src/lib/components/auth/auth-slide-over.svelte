<script lang="ts">
	import { ambientAuth } from '$lib/ambient-auth.svelte';
	import LoginForm from './login-form.svelte';
	import RegisterForm from './register-form.svelte';

	function handleBackdropClick(event: MouseEvent) {
		if (event.target === event.currentTarget) {
			ambientAuth.cancel();
		}
	}

	function handleKeydown(event: KeyboardEvent) {
		if (event.key === 'Escape') {
			ambientAuth.cancel();
		}
	}
</script>

<svelte:window onkeydown={handleKeydown} />

{#if ambientAuth.showOverlay}
	<div
		class="fixed inset-0 z-50 flex items-center justify-center bg-black/40 backdrop-blur-sm p-4 animate-fade-in"
		onclick={handleBackdropClick}
		role="presentation"
	>
		<div
			class="w-full max-w-md rounded-2xl border border-outline-variant bg-surface-container-lowest shadow-xl animate-scale-in"
			role="dialog"
			aria-modal="true"
			aria-label="Authentication required"
		>
			<div class="flex items-center justify-between p-6 pb-2">
				<div class="flex items-center gap-3">
					<div class="flex h-10 w-10 items-center justify-center rounded-xl bg-primary text-on-primary">
						<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M15 3h4a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2h-4"/><polyline points="10 17 15 12 10 7"/><line x1="15" y1="12" x2="3" y2="12"/></svg>
					</div>
					<div>
						<h3 class="text-headline-md font-semibold text-fg">
							{ambientAuth.pendingAction?.label ?? 'Sign in'}
						</h3>
						<p class="text-body-md text-on-surface-variant">
							{ambientAuth.overlayMode === 'login' ? 'Welcome back' : 'Create your account'}
						</p>
					</div>
				</div>
				<button
					onclick={() => ambientAuth.cancel()}
					class="flex h-8 w-8 items-center justify-center rounded-lg text-on-surface-variant hover:bg-surface-container-low hover:text-fg transition-colors"
					aria-label="Close"
				>
					<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>
				</button>
			</div>

			<div class="p-6 pt-4">
				{#if ambientAuth.overlayMode === 'login'}
					<LoginForm />
				{:else}
					<RegisterForm />
				{/if}
			</div>

			<div class="flex items-center justify-center border-t border-outline-variant/60 p-6">
				<p class="text-body-md text-on-surface-variant">
					{ambientAuth.overlayMode === 'login' ? "Don't have an account?" : 'Already have an account?'}
					<button
						onclick={() => ambientAuth.switchMode(ambientAuth.overlayMode === 'login' ? 'register' : 'login')}
						class="ml-1 font-semibold text-primary hover:text-primary-container transition-colors"
					>
						{ambientAuth.overlayMode === 'login' ? 'Sign up' : 'Sign in'}
					</button>
				</p>
			</div>
		</div>
	</div>
{/if}
