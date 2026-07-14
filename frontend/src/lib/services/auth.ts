import { graphqlClient } from '$lib/graphql/client';
import { authStore } from '$lib/stores/auth';
import { LOGIN, REGISTER, LOGOUT, REFRESH_TOKEN, GET_ME, REQUEST_PASSWORD_RESET, CONFIRM_PASSWORD_RESET, SEND_EMAIL_VERIFICATION, VERIFY_EMAIL } from '$lib/graphql/queries/auth';
import type { User } from '$lib/graphql/types';

interface MeResponse {
	me: User | null;
}

interface RefreshTokenResponse {
	refreshToken: { access_token: string };
}

interface LogoutResponse {
	logout: boolean;
}

/**
 * Login user with email and password
 */
export async function login(email: string, password: string): Promise<User> {
	const result = await graphqlClient
		.mutation<{ login: { access_token: string; refresh_token: string } }, { input: { email: string; password: string } }>(
			LOGIN,
			{ input: { email, password } }
		)
		.toPromise();

	if (result.error) {
		throw new Error(result.error.message);
	}

	if (!result.data?.login) {
		throw new Error('Invalid credentials');
	}

	const { access_token, refresh_token } = result.data.login;

	authStore.setTokens(access_token, refresh_token);

	const user = await getMe();
	if (!user) {
		authStore.logout();
		throw new Error('Failed to fetch user profile');
	}

	authStore.setUser(user);
	return user;
}

/**
 * Register a new user
 */
export async function register(
	email: string,
	password: string,
	first_name: string,
	last_name: string
): Promise<User> {
	const result = await graphqlClient
		.mutation<
			{ register: { access_token: string; refresh_token: string } },
			{ input: { email: string; password: string; firstName: string; lastName: string } }
		>(
			REGISTER,
			{ input: { email, password, firstName: first_name, lastName: last_name } }
		)
		.toPromise();

	if (result.error) {
		throw new Error(result.error.message);
	}

	if (!result.data?.register) {
		throw new Error('Registration failed');
	}

	const { access_token, refresh_token } = result.data.register;

	authStore.setTokens(access_token, refresh_token);

	const user = await getMe();
	if (!user) {
		authStore.logout();
		throw new Error('Failed to fetch user profile');
	}

	authStore.setUser(user);
	return user;
}

/**
 * Logout current user
 */
export async function logout(): Promise<void> {
	const stored = authStore.loadFromStorage();
	const token = stored.refreshToken;

	if (token) {
		try {
			await graphqlClient
				.mutation<LogoutResponse, { refresh_token: string }>(
					LOGOUT,
					{ refresh_token: token }
				)
				.toPromise();
		} catch {
			// Ignore server errors during logout
		}
	}

	authStore.logout();
}

/**
 * Refresh access token using refresh token
 */
export async function refreshToken(refresh_token: string): Promise<string> {
	const result = await graphqlClient
		.mutation<RefreshTokenResponse, { refresh_token: string }>(
			REFRESH_TOKEN,
			{ refresh_token }
		)
		.toPromise();

	if (result.error) {
		throw new Error(result.error.message);
	}

	if (!result.data?.refreshToken) {
		throw new Error('Token refresh failed');
	}

	return result.data.refreshToken.access_token;
}

/**
 * Get current user profile
 */
export async function getMe(): Promise<User | null> {
	const result = await graphqlClient
		.query<MeResponse>(GET_ME, {})
		.toPromise();

	if (result.error || !result.data?.me) {
		return null;
	}

	return result.data.me;
}

export async function requestPasswordReset(email: string): Promise<boolean> {
	const result = await graphqlClient
		.mutation<{ request_password_reset: boolean }, { input: { email: string } }>(
			REQUEST_PASSWORD_RESET,
			{ input: { email } }
		)
		.toPromise();
	return result.data?.request_password_reset ?? false;
}

export async function confirmPasswordReset(token: string, newPassword: string): Promise<boolean> {
	const result = await graphqlClient
		.mutation<{ confirm_password_reset: boolean }, { input: { token: string; newPassword: string } }>(
			CONFIRM_PASSWORD_RESET,
			{ input: { token, new_password: newPassword as never } }
		)
		.toPromise();
	return result.data?.confirm_password_reset ?? false;
}

export async function sendEmailVerification(): Promise<boolean> {
	const result = await graphqlClient
		.mutation<{ send_email_verification: boolean }, Record<string, never>>(
			SEND_EMAIL_VERIFICATION,
			{}
		)
		.toPromise();
	return result.data?.send_email_verification ?? false;
}

export async function verifyEmail(token: string): Promise<boolean> {
	const result = await graphqlClient
		.mutation<{ verify_email: boolean }, { input: { token: string } }>(
			VERIFY_EMAIL,
			{ input: { token } }
		)
		.toPromise();
	return result.data?.verify_email ?? false;
}
