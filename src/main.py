from fastapi import FastAPI, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.routers import router
from src.core.config import settings
from src.db.db import get_async_session
from src.db.init_db import create_first_superuser

app = FastAPI(title=settings.title)

app.include_router(router)


@app.get('/ping', tags=['ping'])
async def ping_db(
        session: AsyncSession = Depends(get_async_session)
):
    try:
        await session.execute('SELECT 1')
        return {"status": "Database is available"}
    except Exception as e:
        return {"status": "Database is not available", "error": str(e)}


@app.on_event('startup')
async def startup():
    # Not needed if you setup a migration system like Alembic
    # await create_db_and_tables()
    await create_first_superuser()
