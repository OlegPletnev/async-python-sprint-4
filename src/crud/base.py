from typing import TypeVar, Type

from fastapi_users_db_sqlalchemy import GUID
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.db import Base
from src.models import User

ModelType = TypeVar('ModelType', bound=Base)
CreateSchemaType = TypeVar('CreateSchemaType', bound=BaseModel)


class CRUDBase:
    def __init__(self, model: Type[ModelType]):
        self.model = model

    async def get(
            self,
            *,
            field: str,
            value: GUID | str,
            return_all: bool = False,
            session: AsyncSession):
        db_obj = await session.execute(
            select(self.model)
            .where(getattr(self.model, field) == value)
        )
        if return_all:
            return db_obj.scalars().all()
        else:
            return db_obj.scalars().first()

    async def create(
            self,
            session: AsyncSession,
            obj: CreateSchemaType,
            user: User | None = None,
    ) -> ModelType:
        obj = obj.model_dump()
        if not obj['user_id']:
            obj['user_id'] = user.id
        db_obj = self.model(**obj)
        session.add(db_obj)
        await session.commit()
        await session.refresh(db_obj)
        return db_obj
