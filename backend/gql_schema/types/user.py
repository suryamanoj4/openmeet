import uuid
from datetime import datetime
from typing import Annotated, Optional

import strawberry
from strawberry import lazy


@strawberry.type
class UserType:
    id: uuid.UUID
    email: str
    first_name: Optional[str]
    last_name: Optional[str]
    phone: Optional[str]
    avatar_url: Optional[str]
    is_email_verified: bool
    role: str
    is_superuser: bool
    created_at: datetime
    updated_at: datetime

    @strawberry.field
    async def organizations(
        self, info: strawberry.Info
    ) -> list[Annotated["OrganizationType", lazy("gql_schema.types.organization")]]:
        from gql_schema.services.user_service import UserService

        session = info.context["db"]
        service = UserService(session)
        return await service.get_user_organizations(self.id)

    @strawberry.field
    async def followers(
        self, info: strawberry.Info
    ) -> list[Annotated["FollowerType", lazy("gql_schema.types.follower")]]:
        from gql_schema.services.user_service import UserService

        session = info.context["db"]
        service = UserService(session)
        return await service.get_user_followers(self.id)
