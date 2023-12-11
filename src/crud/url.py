from typing import TypeVar

from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from src.crud.base import CRUDBase
from src.models import ShortURL, ClickURL

UpdateSchemaType = TypeVar('UpdateSchemaType', bound=BaseModel)


class CRUDShortURL(CRUDBase):
    @staticmethod
    async def update(
            db_obj: ShortURL,
            obj_in: UpdateSchemaType,
            session: AsyncSession,
    ):
        obj_data = jsonable_encoder(db_obj)
        update_data = obj_in.model_dump(exclude_unset=True)

        for field in obj_data:
            if field in update_data:
                setattr(db_obj, field, update_data[field])
        session.add(db_obj)
        await session.commit()
        await session.refresh(db_obj)
        return db_obj


url_crud = CRUDShortURL(ShortURL)


class CRUDClickURL(CRUDBase):
    pass


url_click = CRUDClickURL(ClickURL)
