export const CREATE_TICKET = `
	mutation CreateTicket($input: CreateTicketInput!) {
		create_ticket: createTicket(input: $input) {
			id
			name
			price
			currency
			quantity
		}
	}
`;

export const UPDATE_TICKET = `
	mutation UpdateTicket($id: UUID!, $input: UpdateTicketInput!) {
		update_ticket: updateTicket(id: $id, input: $input) {
			id
			name
			price
			quantity
		}
	}
`;

export const DELETE_TICKET = `
	mutation DeleteTicket($id: UUID!) {
		delete_ticket: deleteTicket(id: $id)
	}
`;
