import asyncio
from app.database import engine, Base
from app import models  # noqa

async def recreate():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    await engine.dispose()
    print("Таблицы пересозданы")

if __name__ == "__main__":
    asyncio.run(recreate())