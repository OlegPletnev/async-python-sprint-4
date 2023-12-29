from http import HTTPStatus
from random import choice
from string import ascii_letters, digits
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, Body
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.check import check_exist_id
from src.core.user import current_active_user
from src.crud.url import url_crud, url_click
from src.db.db import get_async_session
from src.models import ShortURL, User
from src.schemas.url import SchemaCreateURL, SchemaCreateClick, \
    SchemaUpdateURL, SchemaURL

router = APIRouter(tags=['short url'])


@router.post(
    '/',
    response_model=SchemaURL,
    response_model_exclude_none=True,
    status_code=HTTPStatus.CREATED,
)
async def create_short_url(
        original_url: Annotated[str, Body()],
        session: AsyncSession = Depends(get_async_session),
        user: User = Depends(current_active_user),
) -> ShortURL:
    """
    Создать и сохранить в базе сокращённый вариант
    переданного в теле запроса оригинального URL
    """
    generated_short_url = ''.join(
        choice(ascii_letters + digits) for _ in range(5)
    )
    obj = SchemaCreateURL(
        original_url=original_url,
        short_url=generated_short_url,
        user_id=user.id
    )

    return await url_crud.create(session, obj, user)


@router.get('/ping', tags=['ping'])
async def ping_db(
        session: AsyncSession = Depends(get_async_session)
):
    try:
        await session.execute(select(func.now()))
        return {"status": "Database is available"}
    except Exception as e:
        return {"status": "Database is not available", "error": str(e)}


@router.get(
    '/{short_id}/status',
    response_model=None,
)
async def get_url_status(
        short_id: UUID,
        full_info: Annotated[bool, Query(alias='full-info')] = False,
        max_result: Annotated[
            int | None, Query(gt=0, alias='max-result')
        ] = 100,
        offset: Annotated[int | None, Query(ge=0)] = None,
        session: AsyncSession = Depends(get_async_session),
):
    """
    Метод принимает в качестве параметра идентификатор сокращённого URL
    и возвращает информацию о количестве переходов, совершенных по ссылке.

    В ответе может содержаться как **общее количество совершенных переходов**,
    так и дополнительная детализированная **информация о каждом переходе**
    (наличие query-параметра full-info и параметров пагинации):

    - дата и время перехода/использования ссылки;
    - информация о клиенте, выполнившем запрос;
    """
    record = await check_exist_id(short_id=short_id, session=session)
    records = await url_click.get(
        field='url_id', value=record.id, return_all=True, session=session)
    if full_info:
        return records[offset:max_result]
    return {'Количество совершенных переходов': len(records)}


@router.get(
    '/{short_id}',
    status_code=HTTPStatus.TEMPORARY_REDIRECT,
)
async def redirect_by_short_url(
        short_id: UUID,
        user: User | None = Depends(current_active_user),
        session: AsyncSession = Depends(get_async_session),
) -> dict[str, str]:
    """
    Метод принимает в качестве параметра идентификатор сокращённого URL
    и возвращает ответ с кодом 307 и оригинальным `URL` в заголовке `Location`.

    Если ссылка приватная, то пользоваться может только user-автор
    """
    record = await check_exist_id(short_id=short_id, session=session)
    if record and record.is_deleted:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail='Вы не можете перейти по удаленной ссылке',
        )
    if (user and user.id != record.user_id and record.type == 'private') or (
            user is None and record.type == 'private'):
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail='Вы не можете перейти по чужой приватной ссылке',
        )
    # original_url = str(url.original_url)
    obj = SchemaCreateClick(url_id=record.id, user_id=user.id)
    await url_click.create(
        obj=obj,
        user=user,
        session=session
    )
    return {'Location': record.original_url}


@router.delete(
    '/{short_id}',
    deprecated=True
)
def delete_short_url():
    """
    Не используйте удаление, деактивируйте короткие ссылки.
    Возможность «удаления» сохранённого URL, реализована в методе PATCH,
    где сама запись остается, но помечается как удалённая
    """
    raise HTTPException(
        # 405 ошибка - метод не разрешен.
        status_code=HTTPStatus.METHOD_NOT_ALLOWED,
        detail="Удаление коротких ссылок запрещено! Просто деактивируйте их."
    )


@router.patch('/{short_id}', response_model=SchemaURL)
async def update_short_url(
        short_id: UUID,
        obj_in: SchemaUpdateURL,
        session: AsyncSession = Depends(get_async_session),
        user: User = Depends(current_active_user),
):
    """
    Метод, позволяющий установить признак удаленной короткой ссылки,
    а так же изменить её видимость для других пользователей.
    """
    record = await check_exist_id(short_id, session)
    if record.user_id != user.id:
        raise HTTPException(
            # 405 ошибка - метод не разрешен.
            status_code=HTTPStatus.METHOD_NOT_ALLOWED,
            detail="Только автор короткой ссылки может менять её тип "
                   "и признак удаления"
        )

    data = await url_crud.update(
        db_obj=record,
        obj_in=obj_in,
        session=session,
    )
    return data
