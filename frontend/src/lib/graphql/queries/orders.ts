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
