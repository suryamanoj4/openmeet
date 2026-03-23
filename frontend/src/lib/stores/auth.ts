import { writable, derived, type Readable } from 'svelte/store';
import { browser } from '$app/environment';
import type { User } from '$lib/graphql/types';

interface AuthState {
	user: User | null;
	accessToken: string | null;
	refreshToken: string | null;
	isLoading: boolean;
	isAuthenticated: boolean;
}

const initialState: AuthState = {
	user: null,
	accessToken: null,
	refreshToken: null,
	isLoading: true,
	isAuthenticated: false
};

function createAuthStore() {
	const { subscribe, set, update } = writable<AuthState>(initialState);

	return {
		subscribe,

		/**
		 * Set the current user
		 */
		setUser(user: User | null) {
			update((state) => ({
				...state,
				user,
				isAuthenticated: user !== null,
				isLoading: false
			}));
		},

		/**
		 * Set auth tokens and persist to localStorage
		 */
		setTokens(accessToken: string, refreshToken: string) {
			if (browser) {
				localStorage.setItem('access_token', accessToken);
				localStorage.setItem('refresh_token', refreshToken);
			}
			update((state) => ({ ...state, accessToken, refreshToken }));
		},

		/**
		 * Set loading state
		 */
		setLoading(loading: boolean) {
			update((state) => ({ ...state, isLoading: loading }));
		},

		/**
		 * Clear auth state and remove tokens from localStorage
		 */
		logout() {
			if (browser) {
				localStorage.removeItem('access_token');
				localStorage.removeItem('refresh_token');
			}
			set(initialState);
		},

		/**
		 * Load tokens from localStorage on app init
		 */
		loadFromStorage(): { accessToken: string | null; refreshToken: string | null } {
			if (!browser) {
				return { accessToken: null, refreshToken: null };
			}

			const accessToken = localStorage.getItem('access_token');
			const refreshToken = localStorage.getItem('refresh_token');

			if (accessToken && refreshToken) {
				update((state) => ({
					...state,
					accessToken,
					refreshToken,
					isLoading: false
				}));
			} else {
				set(initialState);
			}

			return { accessToken, refreshToken };
		},

		/**
		 * Update tokens without persisting (for token refresh)
		 */
		updateTokens(accessToken: string, refreshToken: string) {
			if (browser) {
				localStorage.setItem('access_token', accessToken);
				localStorage.setItem('refresh_token', refreshToken);
			}
			update((state) => ({ ...state, accessToken, refreshToken }));
		}
	};
}

export const authStore = createAuthStore();

/**
 * Derived store to check if user is authenticated
 */
export const isAuthenticated: Readable<boolean> = derived(
	authStore,
	($auth) => $auth.isAuthenticated
);

/**
 * Derived store to get the current user
 */
export const currentUser: Readable<User | null> = derived(
	authStore,
	($auth) => $auth.user
);

/**
 * Derived store to check if auth is still loading
 */
export const authLoading: Readable<boolean> = derived(
	authStore,
	($auth) => $auth.isLoading
);
