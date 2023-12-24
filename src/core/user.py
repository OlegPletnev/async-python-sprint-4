import re
import uuid

from fastapi import Depends
from fastapi_users import (
    BaseUserManager, FastAPIUsers, InvalidPasswordException, UUIDIDMixin
)
from fastapi_users.authentication import (
    BearerTransport, JWTStrategy, AuthenticationBackend
)
from fastapi_users_db_sqlalchemy import SQLAlchemyUserDatabase
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.config import settings
from src.db.db import get_async_session
from src.models import User
from src.schemas.user import UserCreate


async def get_user_db(session: AsyncSession = Depends(get_async_session)):
    yield SQLAlchemyUserDatabase(session, User)


bearer_transport = BearerTransport(tokenUrl='auth/jwt/login')


def get_jwt_strategy() -> JWTStrategy:
    return JWTStrategy(secret=settings.secret, lifetime_seconds=3600)


auth_backend = AuthenticationBackend(
    name='jwt',
    transport=bearer_transport,
    get_strategy=get_jwt_strategy,
)


class UserManager(UUIDIDMixin, BaseUserManager[User, uuid.UUID]):
    reset_password_token_secret = settings.secret
    verification_token_secret = settings.secret

    async def validate_password(self, password: str, user: UserCreate | User):
        if re.search('[а-я]', password, re.IGNORECASE):
            raise ValueError(
                'Пожалуйста, не включайте в password русские буквы'
            )
        if user.email in password:
            raise InvalidPasswordException(
                reason="Password не должен содержать e-mail"
            )


async def get_user_manager(user_db=Depends(get_user_db)):
    yield UserManager(user_db)


fastapi_users = FastAPIUsers[User, int](
    get_user_manager,
    [auth_backend],
)

current_active_user = fastapi_users.current_user(active=True)
current_superuser = fastapi_users.current_user(active=True, superuser=True)
