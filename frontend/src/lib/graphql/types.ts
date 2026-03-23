// GraphQL type definitions matching the backend schema

export interface User {
	id: string;
	email: string;
	first_name: string;
	last_name: string;
	phone?: string;
	avatar_url?: string;
	is_email_verified: boolean;
	created_at: string;
	updated_at: string;
}

export interface Organization {
	id: string;
	name: string;
	slug: string;
	description?: string;
	logo_url?: string;
	website_url?: string;
	social_links?: Record<string, unknown>;
	settings?: Record<string, unknown>;
	is_verified: boolean;
	created_at: string;
	updated_at: string;
}

export interface Member {
	id: string;
	user_id: string;
	organization_id: string;
	role: 'admin' | 'member';
	joined_at: string;
	is_active: boolean;
	created_at: string;
	updated_at: string;
}

export interface Event {
	id: string;
	organization_id: string;
	name: string;
	slug: string;
	description?: string;
	event_type: string;
	status: 'draft' | 'published' | 'cancelled' | 'completed';
	visibility: 'public' | 'private' | 'unlisted';
	start_date: string;
	end_date: string;
	timezone: string;
	venue_name?: string;
	venue_address?: Record<string, unknown>;
	venue_city?: string;
	venue_country?: string;
	is_online: boolean;
	online_url?: string;
	max_attendees?: number;
	min_tickets_per_order: number;
	max_tickets_per_order: number;
	registration_start?: string;
	registration_end?: string;
	cover_image_url?: string;
	banner_image_url?: string;
	settings?: Record<string, unknown>;
	created_at: string;
	updated_at: string;
}

export interface Ticket {
	id: string;
	event_id: string;
	name: string;
	description?: string;
	price: number;
	currency: string;
	quantity: number;
	sold_quantity: number;
	min_per_order: number;
	max_per_order: number;
	sale_start?: string;
	sale_end?: string;
	is_active: boolean;
	created_at: string;
	updated_at: string;
}

export interface Order {
	id: string;
	event_id: string;
	order_number: string;
	status: 'pending' | 'confirmed' | 'cancelled' | 'expired' | 'refunded';
	customer_email: string;
	customer_first_name?: string;
	customer_last_name?: string;
	customer_phone?: string;
	subtotal: number;
	tax_amount: number;
	discount_amount: number;
	total: number;
	currency: string;
	payment_status: 'unpaid' | 'paid' | 'partial' | 'refunded';
	notes?: string;
	created_at: string;
	updated_at: string;
}

export interface Attendee {
	id: string;
	order_item_id: string;
	ticket_id: string;
	first_name: string;
	last_name: string;
	email: string;
	phone?: string;
	company?: string;
	job_title?: string;
	custom_data?: Record<string, unknown>;
	check_in_status: 'not_checked_in' | 'checked_in' | 'cancelled';
	check_in_at?: string;
	check_in_by?: string;
	notes?: string;
	is_active: boolean;
	created_at: string;
	updated_at: string;
}

// Auth-related types
export interface LoginInput {
	email: string;
	password: string;
}

export interface RegisterInput {
	email: string;
	password: string;
	first_name: string;
	last_name: string;
}

export interface AuthTokens {
	access_token: string;
	refresh_token: string;
}

export interface AuthResponse {
	user: User;
	access_token: string;
	refresh_token: string;
}
