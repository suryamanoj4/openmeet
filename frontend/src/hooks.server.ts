import type { Handle } from '@sveltejs/kit';

/**
 * Handle route protection for (app) routes
 * This runs on the server side
 */
export const handle: Handle = async ({ event, resolve }) => {
	// Check if the route is protected (under /app)
	const isProtectedRoute = event.url.pathname.startsWith('/dashboard');

	if (isProtectedRoute) {
		const session = event.locals.session;

		if (!session?.user) {
			// Redirect to login if not authenticated
			return new Response(null, {
				status: 303,
				headers: {
					location: '/login'
				}
			});
		}
	}

	return resolve(event);
};
