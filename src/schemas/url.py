import uuid
from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel


class URLType(StrEnum):
    PUBLIC = 'public'
    PRIVATE = 'private'


class SchemaCreateURL(BaseModel):
    short_url: str
    original_url: str
    user_id: uuid.UUID | None = None
    type: URLType | None = 'public'


class SchemaURL(SchemaCreateURL):
    id: uuid.UUID
    is_deleted: bool = False


class SchemaUpdateURL(BaseModel):
    type: URLType = 'public'
    is_deleted: bool = False


class SchemaCreateClick(BaseModel):
    url_id: uuid.UUID
    user_id: uuid.UUID


class SchemaClick(SchemaCreateClick):
    access_time: datetime = datetime.now()
