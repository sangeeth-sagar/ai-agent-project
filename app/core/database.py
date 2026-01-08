# app/core/database.py
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from psycopg_pool import AsyncConnectionPool # The modern Async driver
from dotenv import load_dotenv

load_dotenv()

# 1. Get URL and ensure it's valid
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    # Fallback to DB_DSN if DATABASE_URL is missing (Backward compatibility)
    DATABASE_URL = os.getenv("DB_DSN")
    
if not DATABASE_URL:
    raise ValueError("❌ CRITICAL ERROR: DATABASE_URL is missing in .env file.")

# --- SYSTEM A: SQLAlchemy (Sync) for Auth ---
# Note: SQLAlchemy needs the "postgresql://" prefix, but some cloud providers use "postgres://"
# This fix ensures compatibility.
SYNC_URL = DATABASE_URL.replace("postgresql+asyncpg://", "postgresql://")

engine = create_engine(SYNC_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    """Dependency for Auth Endpoints (Sync)"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- SYSTEM B: Psycopg Pool (Async) for Chat ---
# We create the pool object here but OPEN it in main.py
pool = AsyncConnectionPool(conninfo=DATABASE_URL, open=False)

async def get_db_connection():
    """
    Dependency for Chat Endpoints (Async).
    Yields a connection from the pool.
    """
    async with pool.connection() as conn:
        yield conn