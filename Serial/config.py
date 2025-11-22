import os
import sys

class Config:
    # Telegram Credentials (Environment Variables se uthenge)
    APP_ID = int(os.environ.get("APP_ID", 31064914))
    API_HASH = os.environ.get("API_HASH", "f6443d977b6ad8979696174c3f6cfd88")
    TG_BOT_TOKEN = os.environ.get("TG_BOT_TOKEN", "8301448875:AAFk8jYF94cIKlRVX4FkMqcxp6hgzjPWoEk")

    # Database & Time
    DATABASE_URL = os.environ.get("DATABASE_URL", "postgresql://serial:serial@localhost:5432/serial_db")
    ZEE5_COOKIES = os.environ.get("ZEE5_COOKIES", "cjConsent=MHxOfDB8Tnww;cjUser=4e8d367e-8d56-46fc-b5ae-e4edc0e67d39;_cnv_id.60de=ac6992ef-f1db-485b-b156-75d431edc0ee.1763792530.4.1763827750.1763813813.48d9a532-8eee-4478-b905-695e57933cae.516d5ce1-1ef8-4d98-aaaf-d2ad06d9f814..;__eoi=ID=756a51bd3355c55d:T=1763792537:RT=1763792537:S=AA-AfjZD7Z8601_-CBc4FSvaWUt-;__gads=ID=2733b53182138c35:T=1763792537:RT=1763800186:S=ALNI_MZsGKt1fhNtGtjY_tiWPosPA8RjTQ;_cnv_ses.60de=*") 
    UPDATE_CHANNEL = os.environ.get("UPDATE_CHANNEL", "-1003386880915") 
    MONITOR_INTERVAL_MINUTES = int(os.environ.get("MONITOR_INTERVAL", 5))
    
    # Storage & Other Settings
    DOWNLOAD_LOCATION = "./DOWNLOADS"
    TG_MAX_FILE_SIZE = 2097152000
    
    if not all([APP_ID, API_HASH, TG_BOT_TOKEN, ZEE5_COOKIES, DATABASE_URL, UPDATE_CHANNEL]):
        print("CRITICAL ERROR: Please set all required environment variables.")
        sys.exit(1)