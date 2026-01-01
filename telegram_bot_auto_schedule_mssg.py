import os
import time
import asyncio
from datetime import datetime

import gspread
import pytz
from dotenv import load_dotenv
from oauth2client.service_account import ServiceAccountCredentials
from telegram import Bot
from apscheduler.schedulers.blocking import BlockingScheduler

# ===== LOAD ENV =====
load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
SHEET_NAME = os.getenv("SHEET_NAME")
TIMEZONE_NAME = os.getenv("TIMEZONE")

# ===== VALIDATE ENV =====
if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN not set in .env")

if not SHEET_NAME:
    raise ValueError("SHEET_NAME not set in .env")

if not TIMEZONE_NAME:
    raise ValueError("TIMEZONE not set in .env")

TIMEZONE = pytz.timezone(TIMEZONE_NAME)

# ===== CONFIG =====
MESSAGE = """📢 Announcement

Tomorrow’s session starts at 10:30 AM.
Please be on time.
"""

SEND_AT = "2026-01-01 15:16"  # YYYY-MM-DD HH:MM (IST)

# ===== INIT =====
bot = Bot(token=BOT_TOKEN)
scheduler = BlockingScheduler(timezone=TIMEZONE)

# ===== GOOGLE SHEETS AUTH =====
scope = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive"
]

creds = ServiceAccountCredentials.from_json_keyfile_name(
    "credentials.json",
    scope
)

client = gspread.authorize(creds)
sheet = client.open(SHEET_NAME).sheet1

# ===== ASYNC SENDER =====
async def send_async(messages):
    for chat_id, text in messages:
        await bot.send_message(chat_id=chat_id, text=text)
        await asyncio.sleep(0.5)

# ===== BROADCAST JOB =====
def send_broadcast():
    users = sheet.get_all_records()
    messages = []

    for user in users:
        if user.get("status") == "ACTIVE":
            messages.append((int(user["chat_id"]), MESSAGE))

    if messages:
        asyncio.run(send_async(messages))

    print("✅ Message sent once. Exiting.")
    scheduler.shutdown(wait=False)

# ===== SCHEDULE =====
run_time = TIMEZONE.localize(
    datetime.strptime(SEND_AT, "%Y-%m-%d %H:%M")
)

scheduler.add_job(send_broadcast, "date", run_date=run_time)

print(f"⏳ Scheduled for {SEND_AT} ({TIMEZONE_NAME})")
scheduler.start()
