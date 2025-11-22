import asyncpg
from config import Config
import asyncio
import logging

logger = logging.getLogger(__name__)

DB_POOL = None

async def init_db_pool():
    """DB connection pool ko shuru karta hai aur table create karta hai."""
    global DB_POOL
    try:
        DB_POOL = await asyncpg.create_pool(dsn=Config.DATABASE_URL, min_size=1, max_size=10)
        logger.info("Database connection pool established successfully.")
        
        async with DB_POOL.acquire() as conn:
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS processed_videos (
                    id SERIAL PRIMARY KEY,
                    video_url TEXT UNIQUE NOT NULL,
                    processed_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
                );
            """)
        
    except Exception as e:
        logger.error(f"Error connecting to database: {e}")
        asyncio.get_event_loop().stop()

async def is_video_processed(video_url: str) -> bool:
    """Check karta hai ki video URL pehle se DB mein hai ya nahi."""
    if not DB_POOL: return True
    async with DB_POOL.acquire() as conn:
        row = await conn.fetchrow("SELECT id FROM processed_videos WHERE video_url = $1", video_url)
    return row is not None

async def add_processed_video(video_url: str):
    """Video URL ko database mein add karta hai."""
    if not DB_POOL: return
    try:
        async with DB_POOL.acquire() as conn:
            await conn.execute(
                "INSERT INTO processed_videos (video_url) VALUES ($1) ON CONFLICT (video_url) DO NOTHING",
                video_url
            )
        logger.info(f"DB: Recorded URL: {video_url}")
    except Exception as e:
        logger.error(f"DB Error while recording: {e}")