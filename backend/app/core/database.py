from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from app.core.config import settings

# Base class for ORM models
Base = declarative_base()

# Create Async Engine
engine = create_async_engine(
    settings.SQLALCHEMY_DATABASE_URI,
    echo=False, # Set to True to see SQL queries in logs
    future=True
)

# Create Session Factory
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False
)

# Dependency for FastAPI Routes
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()

