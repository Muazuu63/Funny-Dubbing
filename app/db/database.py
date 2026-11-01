"""SQLite database connection and session management using aiosqlite."""
import aiosqlite
from pathlib import Path
from app.config import settings

DB_FILE = settings.DATA_DIR / "aivps.db"

async def get_db():
    settings.DATA_DIR.mkdir(parents=True, exist_ok=True)
    async with aiosqlite.connect(DB_FILE) as db:
        await db.execute("PRAGMA foreign_keys = ON;")
        await db.execute("PRAGMA journal_mode = WAL;")
        yield db
