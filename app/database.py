from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from app.config import DB_URL

class Base(DeclarativeBase):
    pass

engine = create_async_engine(DB_URL)

async_session_maker = async_sessionmaker(bind=engine, expire_on_commit=False)

async def get_session():
    async with async_session_maker() as session:
        yield session

async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)