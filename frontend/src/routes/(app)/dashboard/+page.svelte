<script lang="ts">
	import { authStore, currentUser, isAuthenticated } from '$lib/stores/auth';
</script>

<div class="space-y-6">
	<div>
		<h1 class="text-3xl font-bold tracking-tight">Dashboard</h1>
		<p class="text-muted-foreground">
			Welcome to OpenMeets, {$currentUser?.first_name}!
		</p>
	</div>

	<div class="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
		<!-- Placeholder cards for dashboard stats -->
		<div class="rounded-lg border bg-card p-6 shadow-sm">
			<h3 class="text-sm font-medium text-muted-foreground">Organizations</h3>
			<p class="text-2xl font-bold">0</p>
		</div>
		<div class="rounded-lg border bg-card p-6 shadow-sm">
			<h3 class="text-sm font-medium text-muted-foreground">Events</h3>
			<p class="text-2xl font-bold">0</p>
		</div>
		<div class="rounded-lg border bg-card p-6 shadow-sm">
			<h3 class="text-sm font-medium text-muted-foreground">Tickets Sold</h3>
			<p class="text-2xl font-bold">0</p>
		</div>
		<div class="rounded-lg border bg-card p-6 shadow-sm">
			<h3 class="text-sm font-medium text-muted-foreground">Revenue</h3>
			<p class="text-2xl font-bold">$0</p>
		</div>
	</div>

	<div class="rounded-lg border bg-card p-6 shadow-sm">
		<h2 class="text-xl font-semibold mb-4">Getting Started</h2>
		<ol class="list-decimal list-inside space-y-2 text-muted-foreground">
			<li>Create your first organization</li>
			<li>Add team members to your organization</li>
			<li>Create an event</li>
			<li>Set up ticket types</li>
			<li>Share your event and start selling tickets</li>
		</ol>
	</div>
</div>
