from http import HTTPStatus
from uuid import UUID

from fastapi import HTTPException
from fastapi_users_db_sqlalchemy import GUID
from sqlalchemy.ext.asyncio import AsyncSession

from src.crud.url import url_crud
from src.models import ShortURL


async def check_exist_id(
        short_id: UUID,
        session: AsyncSession,
) -> ShortURL:
    record = await url_crud.get(field='id', value=short_id, session=session)
    if not record:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail=f'{short_id}: под этот id нет сокращенного url!'
        )
    return record
