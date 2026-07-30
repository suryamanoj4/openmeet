export const ORDERS = `
	query Orders($event_id: UUID, $limit: Int, $skip: Int) {
		orders(eventId: $event_id, limit: $limit, skip: $skip) {
			id
			order_number: orderNumber
			status
			customer_email: customerEmail
			customer_name: customerName
			total_amount: totalAmount
			currency
			payment_status: paymentStatus
			created_at: createdAt
		}
	}
`;

export const ORDER = `
	query Order($id: UUID!) {
		order(id: $id) {
			id
			event_id: eventId
			order_number: orderNumber
			status
			customer_email: customerEmail
			customer_name: customerName
			customer_phone: customerPhone
			subtotal
			tax_amount: taxAmount
			discount_amount: discountAmount
			total_amount: totalAmount
			currency
			payment_status: paymentStatus
			notes
			created_at: createdAt
			confirmed_at: confirmedAt
		}
	}
`;

export const CREATE_ORDER = `
	mutation CreateOrder($input: CreateOrderInput!) {
		create_order: createOrder(input: $input) {
			id
			order_number: orderNumber
			status
			total_amount: totalAmount
			currency
			payment_status: paymentStatus
		}
	}
`;

export const CONFIRM_ORDER = `
	mutation ConfirmOrder($id: UUID!) {
		confirm_order: confirmOrder(id: $id) {
			id
			status
			payment_status: paymentStatus
		}
	}
`;

export const CREATE_PAYMENT_ORDER = `
	mutation CreatePaymentOrder($order_id: UUID!) {
		payment: createPaymentOrder(orderId: $order_id) {
			provider_order_id: providerOrderId
			provider_key_id: providerKeyId
			order_id: orderId
			order_number: orderNumber
			amount
			currency
		}
	}
`;

export const VERIFY_PAYMENT = `
	mutation VerifyPayment(
		$order_id: UUID!,
		$provider_payment_id: String!,
		$provider_order_id: String!,
		$signature: String!
	) {
		verification: verifyPayment(
			orderId: $order_id,
			providerPaymentId: $provider_payment_id,
			providerOrderId: $provider_order_id,
			signature: $signature
		) {
			success
			order_id: orderId
			payment_status: paymentStatus
			message
		}
	}
`;
