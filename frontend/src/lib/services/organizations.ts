import { graphqlClient } from '$lib/graphql/client';
import { ORGANIZATIONS, ORGANIZATION, ORGANIZATION_MEMBERS, CREATE_ORGANIZATION, UPDATE_ORGANIZATION, ADD_ORG_MEMBER } from '$lib/graphql/queries/organizations';
import type { Organization } from '$lib/graphql/types';

interface OrgsResponse { organizations: Organization[] }
interface OrgResponse { organization: Organization | null }
interface MembersResponse { organization_members: { id: string; user_id: string; role: string; is_active: boolean }[] }

export async function listOrganizations(limit = 50, skip = 0): Promise<Organization[]> {
	const r = await graphqlClient.query<OrgsResponse>(ORGANIZATIONS, { limit, skip }).toPromise();
	return r.data?.organizations ?? [];
}

export async function getOrganization(id: string): Promise<Organization | null> {
	const r = await graphqlClient.query<OrgResponse>(ORGANIZATION, { id }).toPromise();
	return r.data?.organization ?? null;
}

export async function getMembers(orgId: string): Promise<MembersResponse['organization_members']> {
	const r = await graphqlClient.query<MembersResponse>(ORGANIZATION_MEMBERS, { organization_id: orgId }).toPromise();
	return r.data?.organization_members ?? [];
}

export async function createOrganization(input: Record<string, unknown>): Promise<{ id: string; name: string } | null> {
	const r = await graphqlClient.mutation<{ create_organization: { id: string; name: string } }>(CREATE_ORGANIZATION, { input }).toPromise();
	return r.data?.create_organization ?? null;
}

export async function updateOrganization(id: string, input: Record<string, unknown>): Promise<{ id: string; name: string } | null> {
	const r = await graphqlClient.mutation<{ update_organization: { id: string; name: string } }>(UPDATE_ORGANIZATION, { id, input }).toPromise();
	return r.data?.update_organization ?? null;
}

export async function addMember(orgId: string, userId: string, role = 'member'): Promise<boolean> {
	const r = await graphqlClient.mutation<{ add_organization_member: boolean }>(ADD_ORG_MEMBER, { organization_id: orgId, user_id: userId, role }).toPromise();
	return r.data?.add_organization_member ?? false;
}
