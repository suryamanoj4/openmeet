export const GET_ME = `
	query GetMe {
		me {
			id
			email
			first_name: firstName
			last_name: lastName
			phone
			avatar_url: avatarUrl
			is_email_verified: isEmailVerified
			role
			is_superuser: isSuperuser
			created_at: createdAt
			updated_at: updatedAt
		}
	}
`;

export const LOGIN = `
	mutation Login($input: LoginInput!) {
		login(input: $input) {
			access_token: accessToken
			refresh_token: refreshToken
			user_id: userId
			email
			role
			is_superuser: isSuperuser
		}
	}
`;

export const REGISTER = `
	mutation Register($input: RegisterInput!) {
		register(input: $input) {
			access_token: accessToken
			refresh_token: refreshToken
			user_id: userId
			email
			role
			is_superuser: isSuperuser
		}
	}
`;

export const REFRESH_TOKEN = `
	mutation RefreshToken($refresh_token: String!) {
		refreshToken(refresh_token: $refresh_token) {
			access_token: accessToken
		}
	}
`;

export const LOGOUT = `
	mutation Logout($refresh_token: String!) {
		logout(refresh_token: $refresh_token)
	}
`;

export const REQUEST_PASSWORD_RESET = `
	mutation RequestPasswordReset($input: PasswordResetRequestInput!) {
		request_password_reset: requestPasswordReset(input: $input)
	}
`;

export const CONFIRM_PASSWORD_RESET = `
	mutation ConfirmPasswordReset($input: PasswordResetConfirmInput!) {
		confirm_password_reset: confirmPasswordReset(input: $input)
	}
`;

export const SEND_EMAIL_VERIFICATION = `
	mutation SendEmailVerification {
		send_email_verification: sendEmailVerification
	}
`;

export const VERIFY_EMAIL = `
	mutation VerifyEmail($input: EmailVerificationInput!) {
		verify_email: verifyEmail(input: $input)
	}
`;
