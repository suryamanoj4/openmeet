import { graphqlClient } from '$lib/graphql/client';
import { requireMutationResult } from '$lib/graphql/result';
import { ORDERS, ORDER, CREATE_ORDER, CONFIRM_ORDER, CREATE_PAYMENT_ORDER, VERIFY_PAYMENT } from '$lib/graphql/queries/orders';

interface OrderSummary { id: string; order_number: string; status: string; customer_email: string; customer_name: string; total_amount: number; currency: string; payment_status: string }

export async function listOrders(eventId?: string): Promise<OrderSummary[]> {
	const r = await graphqlClient.query<{ orders: OrderSummary[] }>(ORDERS, { event_id: eventId || null }).toPromise();
	return requireMutationResult(r, 'orders', 'Failed to load orders');
}

export async function getOrder(id: string): Promise<Record<string, unknown> | null> {
	const r = await graphqlClient.query<{ order: Record<string, unknown> | null }>(ORDER, { id }).toPromise();
	if (r.error) throw new Error(r.error.message);
	return r.data?.order ?? null;
}

export async function createOrder(input: Record<string, unknown>): Promise<{ id: string; order_number: string; status: string; total_amount: number; currency: string; payment_status: string }> {
	const r = await graphqlClient.mutation<{ create_order: { id: string; order_number: string; status: string; total_amount: number; currency: string; payment_status: string } }>(CREATE_ORDER, { input }).toPromise();
	return requireMutationResult(r, 'create_order', 'Failed to create order');
}

export async function confirmOrder(id: string): Promise<{ id: string; status: string; payment_status: string } | null> {
	const r = await graphqlClient.mutation<{ confirm_order: { id: string; status: string; payment_status: string } }>(CONFIRM_ORDER, { id }).toPromise();
	return requireMutationResult(r, 'confirm_order', 'Failed to confirm order');
}

export async function createPaymentOrder(orderId: string) {
	const r = await graphqlClient.mutation<{ payment: { provider_order_id: string; provider_key_id: string; order_id: string; order_number: string; amount: number; currency: string } }>(
		CREATE_PAYMENT_ORDER,
		{ order_id: orderId }
	).toPromise();
	return requireMutationResult(r, 'payment', 'Failed to initialize payment');
}

export async function verifyPayment(input: {
	order_id: string;
	provider_payment_id: string;
	provider_order_id: string;
	signature: string;
}) {
	const r = await graphqlClient.mutation<{ verification: { success: boolean; payment_status: string; message: string } }>(
		VERIFY_PAYMENT,
		input
	).toPromise();
	return requireMutationResult(r, 'verification', 'Failed to verify payment');
}
