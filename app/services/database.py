import os
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.pool import NullPool
from contextlib import asynccontextmanager

# Get database URL from environment variables
# For testing purposes, we'll use SQLite instead of PostgreSQL
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./test.db")
print(f"Using DATABASE_URL: {DATABASE_URL}")

# If PostgreSQL is configured, convert to async format
if DATABASE_URL.startswith("postgresql://"):
    DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://")
    print(f"Converted DATABASE_URL: {DATABASE_URL}")

# For SQLite, add check_same_thread=False
connect_args = {}
if DATABASE_URL.startswith("sqlite"):
    connect_args = {"check_same_thread": False}

# Create async engine
engine = create_async_engine(
    DATABASE_URL,
    echo=os.getenv("DEBUG", "False").lower() == "true",
    future=True,
    poolclass=NullPool,
    connect_args=connect_args,
)

# Create async session factory
AsyncSessionLocal = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)

# Create base class for models
Base = declarative_base()

# Dependency to get database session
async def get_db():
    """
    Dependency function that yields a SQLAlchemy async session
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()

# Context manager for database session
@asynccontextmanager
async def db_session():
    """
    Context manager for database session
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()

# Initialize database
async def init_db():
    """
    Initialize database connection
    """
    # In a production environment, you might want to use Alembic for migrations
    # This is a simple initialization for development
    async with engine.begin() as conn:
        # Uncomment the following line to create tables on startup (development only)
        # await conn.run_sync(Base.metadata.create_all)
        pass

# Close database connection
async def close_db():
    """
    Close database connection
    """
    await engine.dispose()