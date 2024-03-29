from fastapi import FastAPI

from src.api.routers import router
from src.core.config import settings
from src.db.init_db import create_first_superuser

app = FastAPI(title=settings.project_title)

app.include_router(router)


@app.on_event('startup')
async def startup():
    # Not needed if you setup a migration system like Alembic
    # await create_db_and_tables()
    await create_first_superuser()
