"""Base service for all domain services."""

from typing import Generic, TypeVar, Type, Optional, List
from uuid import UUID

from sqlmodel import select, func
from sqlmodel.ext.asyncio.session import AsyncSession

ModelType = TypeVar("ModelType")


class BaseService(Generic[ModelType]):
    """Base service providing common database operations."""

    def __init__(self, session: AsyncSession):
        self._session = session

    @property
    def session(self) -> AsyncSession:
        return self._session

    async def get_by_id(self, model: Type[ModelType], id: UUID) -> Optional[ModelType]:
        result = await self.session.exec(select(model).where(model.id == id))
        return result.first()

    async def get_all(
        self,
        model: Type[ModelType],
        skip: int = 0,
        limit: int = 100,
    ) -> List[ModelType]:
        result = await self.session.exec(select(model).offset(skip).limit(limit))
        return list(result.all())

    async def count(self, model: Type[ModelType]) -> int:
        result = await self.session.exec(select(func.count()).select_from(model))
        return result.one()

    async def create(self, model: Type[ModelType], **kwargs) -> ModelType:
        instance = model(**kwargs)
        self.session.add(instance)
        await self.session.flush()
        await self.session.refresh(instance)
        return instance

    async def update(self, instance: ModelType, **kwargs) -> ModelType:
        for key, value in kwargs.items():
            setattr(instance, key, value)
        await self.session.flush()
        await self.session.refresh(instance)
        return instance

    async def delete(self, instance: ModelType) -> None:
        await self.session.delete(instance)
        await self.session.flush()