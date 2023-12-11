from fastapi_users_db_sqlalchemy import GUID
from sqlalchemy import Column, ForeignKey, DateTime, String, Boolean, func
from sqlalchemy.orm import relationship

from src.db.db import Base


class ShortURL(Base):
    user_id = Column(
        GUID,
        ForeignKey('user.id', name='user_created_short_url')
    )
    short_url = Column(String(5), unique=True)
    original_url = Column(String(300))
    type = Column(String(10), default='public')
    is_deleted = Column(Boolean, default=False)
    click_on = relationship('ClickURL', cascade='delete')


class ClickURL(Base):
    access_time = Column(DateTime, default=func.now())
    url_id = Column(
        GUID,
        ForeignKey('shorturl.id'),
    )
    user_id = Column(
        GUID,
        ForeignKey('user.id', name='user_click_on_url'),
    )
