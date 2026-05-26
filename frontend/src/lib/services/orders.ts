import { graphqlClient } from '$lib/graphql/client';
import { ORDERS, ORDER, CREATE_ORDER, CONFIRM_ORDER } from '$lib/graphql/queries/orders';

interface OrderSummary { id: string; order_number: string; status: string; customer_email: string; customer_name: string; total_amount: number; currency: string; payment_status: string }

export async function listOrders(eventId?: string): Promise<OrderSummary[]> {
	const r = await graphqlClient.query<{ orders: OrderSummary[] }>(ORDERS, { event_id: eventId || null }).toPromise();
	return r.data?.orders ?? [];
}

export async function getOrder(id: string): Promise<Record<string, unknown> | null> {
	const r = await graphqlClient.query<{ order: Record<string, unknown> | null }>(ORDER, { id }).toPromise();
	return r.data?.order ?? null;
}

export async function createOrder(input: Record<string, unknown>): Promise<{ id: string; order_number: string; status: string } | null> {
	const r = await graphqlClient.mutation<{ create_order: { id: string; order_number: string; status: string } }>(CREATE_ORDER, { input }).toPromise();
	return r.data?.create_order ?? null;
}

export async function confirmOrder(id: string): Promise<{ id: string; status: string; payment_status: string } | null> {
	const r = await graphqlClient.mutation<{ confirm_order: { id: string; status: string; payment_status: string } }>(CONFIRM_ORDER, { id }).toPromise();
	return r.data?.confirm_order ?? null;
}
