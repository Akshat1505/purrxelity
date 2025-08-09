from sqlalchemy.ext.asyncio import create_async_engine,async_sessionmaker
from sqlalchemy.orm import declarative_base

SQLALCHEMY_DATABASE_URL = "sqlite+aiosqlite:///./test.db"
engine=create_async_engine(SQLALCHEMY_DATABASE_URL)

SessionLocal=async_sessionmaker(autocommit=False,autoflush=False,bind=engine)
Base=declarative_base()

async def get_db():
    async with SessionLocal() as session: 
        yield session
