import asyncio
import time
import requests
from bs4 import BeautifulSoup
from pyrogram import Client
from pyrogram.errors import FloodWait
from datetime import datetime, timedelta
import os
import shutil
import subprocess
import logging # Logging ke liye
import sys
import re

logger = logging.getLogger(__name__)

from config import Config
from database.db import is_video_processed, add_processed_video 

# =========================================================
# 1. ZEE5 SCRAPING FUNCTION
# =========================================================

def scrape_new_zee5_links(user_cookies: str) -> list:
    """
    zee5.com se latest video links aur unke upload time nikalta hai.
    Return format: [(url: str, upload_time: datetime), ...]
    """
    
    LATEST_CONTENT_URL = "https://www.zee5.com/tv-shows/genre/drama/hindi" 
    headers = {'Cookie': user_cookies, 'User-Agent': 'Mozilla/5.0'}
    video_data_list = []
    
    try:
        response = requests.get(LATEST_CONTENT_URL, headers=headers, timeout=15)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # --- FINALIZED SCRAPING STRUCTURE ---
        tray_content = soup.find('div', class_='trayContentWrap') 
        if not tray_content: return []
        main_list_wrapper = tray_content.find('div', class_='movieTrayWrapper') 
        if not main_list_wrapper: return []
        video_containers = main_list_wrapper.find_all('div', class_='slick-slide') 
        
        for container in video_containers:
            a_tag = container.find('a', href=True) 
            
            if a_tag:
                href = a_tag.get('href')
                if href and 'video/' in href: 
                    # 🚨 TIMESTAMP PLACEHOLDER: Yahan asli logic aayegi
                    upload_time = datetime.now() - timedelta(hours=3) # Dummy Time
                    
                    if not href.startswith('http'):
                        full_url = f"https://www.zee5.com{href}"  
                    else:
                        full_url = href
                        
                    video_data_list.append((full_url, upload_time))
                    
        return video_data_list
    
    except requests.exceptions.RequestException as e:
        logger.error(f"Scraping Error: {e}")
        return []
    except Exception as e:
        logger.error(f"Parsing Error: {e}")
        return []

# =========================================================
# 2. CORE DOWNLOAD/UPLOAD/DELETE FUNCTION
# =========================================================

async def download_and_upload(client: Client, url: str):
    """ Video download karta hai, Telegram par upload karta hai, aur delete karta hai. """
    
    temp_dir = f"{Config.DOWNLOAD_LOCATION}/{os.getpid()}_{time.time()}"
    os.makedirs(temp_dir, exist_ok=True)
    download_path = f"{temp_dir}/video.mp4"
    
    # 🚨 720P RESOLUTION AUR DOWNLOAD COMMAND 🚨
    command_to_exec = [
        "youtube-dl",
        "-f", "bestvideo[height<=720]+bestaudio/best[height<=720]", # 720p Max
        "--no-warnings",
        url,
        "-o", download_path
    ]
    
    try:
        # Download Execution
        process = await asyncio.create_subprocess_exec(*command_to_exec, 
                                                       stdout=subprocess.PIPE, 
                                                       stderr=subprocess.PIPE)
        await process.wait()
        
        if not os.path.exists(download_path):
            raise Exception("Download failed or file not found.")
            
        video_name = os.path.basename(url).split('/')[-1] 
        
        # UPLOAD TO TELEGRAM (No Thumbnail)
        await client.send_video(
            chat_id=Config.UPDATE_CHANNEL,
            video=download_path,
            caption=f"✅ **{video_name}** uploaded successfully.",
            supports_streaming=True
        )
        
        return True # Success
        
    except Exception as e:
        logger.error(f"Download/Upload Failed for {url}: {e}")
        return False
        
    finally:
        # 🚨 STORAGE CLEANUP (Upload ke turant baad)
        try:
            shutil.rmtree(temp_dir)
            logger.info(f"Cleanup: Deleted temp directory {temp_dir}")
        except Exception as e:
            logger.error(f"Cleanup Failed: {e}")

# =========================================================
# 3. MONITORING SCHEDULER
# =========================================================

async def start_monitoring_loop(client: Client):
    """ Main scheduler jo har 5 min mein scan karta hai. """
    interval = Config.MONITOR_INTERVAL_MINUTES
    
    # Bot start hone par channel par message bhejein
    await client.send_message(
        chat_id=Config.UPDATE_CHANNEL,
        text=f"✅ Automation Started: ZEE5 Monitor checking every {interval} minutes."
    )
    
    while True:
        video_items = scrape_new_zee5_links(Config.ZEE5_COOKIES)
        twenty_four_hours_ago = datetime.now() - timedelta(hours=24)
        
        for url, upload_time in video_items:
            
            if await is_video_processed(url):
                continue 
                
            # 24-hour window check
            if upload_time >= twenty_four_hours_ago:
                logger.info(f"NEW VIDEO FOUND: {url}. Starting process.")
                
                success = await download_and_upload(client, url)
                
                if success:
                    await add_processed_video(url) 
                    
            else:
                # Purana video record karke skip karein
                await add_processed_video(url)
                
        await asyncio.sleep(interval * 60)