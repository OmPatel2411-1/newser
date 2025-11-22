import asyncio
import logging
from pyrogram import Client, idle
import sys

# Custom Imports
from config import Config
from database.db import init_db_pool 
from plugins.autodl import start_monitoring_loop 

logger = logging.getLogger(__name__)

async def main():
    # Database Pool Initialize Karein
    await init_db_pool() 
    
    # Client Initialization (using the correct APP_ID/API_HASH names)
    client = Client(
        "bot_session", 
        api_id=Config.APP_ID,
        api_hash=Config.API_HASH,
        bot_token=Config.TG_BOT_TOKEN,
        plugins=dict(root="plugins")
    )

    await client.start()

    # Monitoring scheduler ko background task mein shuru karein
    asyncio.create_task(start_monitoring_loop(client)) 

    await idle() 
    
    await client.stop()

if __name__ == "__main__":
    # Python 3.7+ mein async function run karne ka tareeka
    asyncio.run(main())