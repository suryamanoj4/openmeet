import type { User } from '$lib/graphql/types';

declare global {
	namespace App {
		interface Locals {
			session: {
				access_token: string;
				refresh_token: string;
				user: User | null;
			} | null;
		}
	}
}

export {};
