"""
Database connection and session management using aiosqlite with Dual Durability Policy.
Master Architecture v2.2 & PRD v2.2 Aligned.
"""
import aiosqlite
from contextlib import asynccontextmanager
from typing import AsyncGenerator
from app.config import settings

DATABASE_PATH = settings.DATABASE_PATH


async def get_connection(critical: bool = False) -> aiosqlite.Connection:
    """
    Creates and configures an aiosqlite connection.
    Dual Durability Policy:
    - Critical Checkpoint Transactions: PRAGMA synchronous = FULL
    - Non-critical Transactions (telemetry, logs): PRAGMA synchronous = NORMAL
    """
    settings.STORAGE_DIR.mkdir(parents=True, exist_ok=True)
    db = await aiosqlite.connect(DATABASE_PATH)
    
    # Configure SQLite pragmas
    await db.execute("PRAGMA journal_mode = WAL;")
    await db.execute("PRAGMA foreign_keys = ON;")
    await db.execute("PRAGMA busy_timeout = 10000;")  # 10s busy wait
    
    if critical:
        await db.execute("PRAGMA synchronous = FULL;")
    else:
        await db.execute("PRAGMA synchronous = NORMAL;")
        
    db.row_factory = aiosqlite.Row
    return db


@asynccontextmanager
async def get_db(critical: bool = False) -> AsyncGenerator[aiosqlite.Connection, None]:
    """
    Async context manager providing a configured aiosqlite connection.
    Ensures safe commit/rollback and connection cleanup.
    """
    conn = await get_connection(critical=critical)
    try:
        yield conn
    except Exception:
        await conn.rollback()
        raise
    finally:
        await conn.close()


async def verify_json1_support(db: aiosqlite.Connection) -> bool:
    """Verifies that SQLite JSON1 extension/functions are available."""
    async with db.execute("SELECT json_extract('{\"check\": 1}', '$.check') AS val;") as cursor:
        row = await cursor.fetchone()
        return bool(row and row[0] == 1)
