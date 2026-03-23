import { graphqlClient } from '$lib/graphql/client';
import { authStore } from '$lib/stores/auth';
import type { LoginInput, RegisterInput, AuthResponse } from '$lib/graphql/types';

interface LoginMutation {
	login: AuthResponse;
}

interface RegisterMutation {
	register: AuthResponse;
}

interface RefreshTokenMutation {
	refreshToken: {
		access_token: string;
		refresh_token: string;
	};
}

interface LogoutMutation {
	logout: boolean;
}

/**
 * Login user with email and password
 */
export async function login(email: string, password: string): Promise<AuthResponse> {
	const result = await graphqlClient
		.mutation<LoginMutation, LoginInput>(
			`
			mutation Login($email: String!, $password: String!) {
				login(email: $email, password: $password) {
					user {
						id
						email
						first_name
						last_name
						avatar_url
						is_email_verified
					}
					access_token
					refresh_token
				}
			}
		`,
			{ email, password }
		)
		.toPromise();

	if (result.error) {
		throw new Error(result.error.message);
	}

	if (!result.data?.login) {
		throw new Error('Login failed');
	}

	const { user, access_token, refresh_token } = result.data.login;

	// Store tokens and user
	authStore.setTokens(access_token, refresh_token);
	authStore.setUser(user);

	return { user, access_token, refresh_token };
}

/**
 * Register a new user
 */
export async function register(
	email: string,
	password: string,
	first_name: string,
	last_name: string
): Promise<AuthResponse> {
	const result = await graphqlClient
		.mutation<RegisterMutation, { input: RegisterInput }>(
			`
			mutation Register($input: RegisterInput!) {
				register(input: $input) {
					user {
						id
						email
						first_name
						last_name
						avatar_url
						is_email_verified
					}
					access_token
					refresh_token
				}
			}
		`,
			{ input: { email, password, first_name, last_name } }
		)
		.toPromise();

	if (result.error) {
		throw new Error(result.error.message);
	}

	if (!result.data?.register) {
		throw new Error('Registration failed');
	}

	const { user, access_token, refresh_token } = result.data.register;

	// Store tokens and user
	authStore.setTokens(access_token, refresh_token);
	authStore.setUser(user);

	return { user, access_token, refresh_token };
}

/**
 * Logout current user
 */
export async function logout(): Promise<void> {
	try {
		await graphqlClient
			.mutation<LogoutMutation, {}>(
				`
				mutation Logout {
					logout
				}
			`,
				{}
			)
			.toPromise();
	} catch (error) {
		// Ignore errors during logout, still clear local state
		console.error('Logout error:', error);
	} finally {
		authStore.logout();
	}
}

/**
 * Refresh access token using refresh token
 */
export async function refreshToken(refreshToken: string): Promise<{
	access_token: string;
	refresh_token: string;
}> {
	const result = await graphqlClient
		.mutation<RefreshTokenMutation, { refresh_token: string }>(
			`
			mutation RefreshToken($refresh_token: String!) {
				refreshToken(refresh_token: $refresh_token) {
					access_token
					refresh_token
				}
			}
		`,
			{ refresh_token: refreshToken }
		)
		.toPromise();

	if (result.error) {
		throw new Error(result.error.message);
	}

	if (!result.data?.refreshToken) {
		throw new Error('Token refresh failed');
	}

	const { access_token, refresh_token } = result.data.refreshToken;

	// Update tokens in store and localStorage
	authStore.updateTokens(access_token, refresh_token);

	return { access_token, refresh_token };
}

/**
 * Get current user profile
 */
export async function getMe(): Promise<{
	id: string;
	email: string;
	first_name: string;
	last_name: string;
	phone?: string;
	avatar_url?: string;
	is_email_verified: boolean;
} | null> {
	const result = await graphqlClient
		.query<{
			me: {
				id: string;
				email: string;
				first_name: string;
				last_name: string;
				phone?: string;
				avatar_url?: string;
				is_email_verified: boolean;
			};
		}>(
			`
			query GetMe {
				me {
					id
					email
					first_name
					last_name
					phone
					avatar_url
					is_email_verified
				}
			}
		`,
			{}
		)
		.toPromise();

	if (result.error || !result.data?.me) {
		return null;
	}

	return result.data.me;
}
