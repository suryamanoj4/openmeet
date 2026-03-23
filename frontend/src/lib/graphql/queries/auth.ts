// GraphQL queries for authentication and user data
import { gql } from '@urql/svelte';

export const GET_ME = gql`
	query GetMe {
		me {
			id
			email
			first_name
			last_name
			phone
			avatar_url
			is_email_verified
			created_at
			updated_at
		}
	}
`;

export const LOGIN = gql`
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
`;

export const REGISTER = gql`
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
`;

export const REFRESH_TOKEN = gql`
	mutation RefreshToken($refresh_token: String!) {
		refreshToken(refresh_token: $refresh_token) {
			access_token
			refresh_token
		}
	}
`;

export const LOGOUT = gql`
	mutation Logout {
		logout
	}
`;

export const REQUEST_PASSWORD_RESET = gql`
	mutation RequestPasswordReset($email: String!) {
		requestPasswordReset(email: $email)
	}
`;

export const RESET_PASSWORD = gql`
	mutation ResetPassword($token: String!, $new_password: String!) {
		resetPassword(token: $token, new_password: $new_password)
	}
`;

export const UPDATE_PROFILE = gql`
	mutation UpdateProfile($input: ProfileInput!) {
		updateProfile(input: $input) {
			id
			email
			first_name
			last_name
			phone
			avatar_url
			is_email_verified
		}
	}
`;

export const CHANGE_PASSWORD = gql`
	mutation ChangePassword($current_password: String!, $new_password: String!) {
		changePassword(current_password: $current_password, new_password: $new_password)
	}
`;
