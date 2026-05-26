export const ORGANIZATIONS = `
	query Organizations($limit: Int, $skip: Int) {
		organizations(limit: $limit, skip: $skip) {
			id
			name
			slug
			description
			logo_url: logoUrl
			website_url: websiteUrl
			is_verified: isVerified
		}
	}
`;

export const ORGANIZATION = `
	query Organization($id: UUID!) {
		organization(id: $id) {
			id
			name
			slug
			description
			logo_url: logoUrl
			website_url: websiteUrl
			social_links: socialLinks
			settings
			is_verified: isVerified
		}
	}
`;

export const ORGANIZATION_MEMBERS = `
	query OrganizationMembers($organization_id: UUID!) {
		organization_members(organizationId: $organization_id) {
			id
			user_id: userId
			role
			joined_at: joinedAt
			is_active: isActive
		}
	}
`;

export const CREATE_ORGANIZATION = `
	mutation CreateOrganization($input: CreateOrganizationInput!) {
		create_organization: createOrganization(input: $input) {
			id
			name
			slug
		}
	}
`;

export const UPDATE_ORGANIZATION = `
	mutation UpdateOrganization($id: UUID!, $input: UpdateOrganizationInput!) {
		update_organization: updateOrganization(id: $id, input: $input) {
			id
			name
			slug
		}
	}
`;

export const ADD_ORG_MEMBER = `
	mutation AddOrganizationMember($organization_id: UUID!, $user_id: UUID!, $role: String!) {
		add_organization_member: addOrganizationMember(organizationId: $organization_id, userId: $user_id, role: $role)
	}
`;
