from fastapi_users_db_sqlalchemy import SQLAlchemyBaseUserTableUUID

from src.db.db import Base


class User(SQLAlchemyBaseUserTableUUID, Base):
    pass
