from http import HTTPStatus

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.user import fastapi_users, auth_backend, current_active_user
from src.crud.url import url_crud
from src.db.db import get_async_session
from src.models import User, ShortURL
from src.schemas.user import UserRead, UserCreate, UserUpdate

router = APIRouter()

router.include_router(
    fastapi_users.get_auth_router(auth_backend),
    prefix="/auth/jwt",
    tags=["auth"]
)
router.include_router(
    fastapi_users.get_register_router(UserRead, UserCreate),
    prefix="/auth",
    tags=["auth"],
)
router.include_router(
    fastapi_users.get_reset_password_router(),
    prefix="/auth",
    tags=["auth"],
)
router.include_router(
    fastapi_users.get_verify_router(UserRead),
    prefix="/auth",
    tags=["auth"],
)
router.include_router(
    fastapi_users.get_users_router(UserRead, UserUpdate),
    prefix="/users",
    tags=["users"],
)


@router.get(
    '/user/status',
    tags=['users'],
    response_model=list[ShortURL] | None,
)
async def get_user_status(
        user: User = Depends(current_active_user),
        session: AsyncSession = Depends(get_async_session),
):
    """
    Метод возвращает все созданные ранее user'ом ссылки
    """
    urls = await session.execute(
        select(ShortURL)
        .where(ShortURL.user_id == user.id)
    )
    if not urls:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail='Укороченные ссылки отсутствуют'
        )
    return urls.scalars().all()

