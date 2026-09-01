import asyncio
from aiogram import Bot
from aiogram.types import BufferedInputFile
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

# --- SOZLAMALAR ---
BOT_TOKEN = "SIZNING_BOT_TOKENINGIZ"

CHAT_ID_48 = -1002717046752
CHAT_ID_34 = -1004397692925
# CHAT_ID_ZAMIN = -100XXXXXXXXXX

SHEET_ID = "1xBro7Q_Bn-FnABrvTQQooL_2fSoxobMi"

PAGES = [
    {
        "chat_id": CHAT_ID_48,
        "sheet_name": "Stanoklar bo'yicha",
        "range": "A1:Z35",
        "caption": "📊 Kunlik Stanoklar hisoboti"
    },
    {
        "chat_id": CHAT_ID_34,
        "sheet_name": "Kunlik krim 34",
        "range": "A1:H35",
        "caption": "📊 Kunlik Krim (34) hisoboti"
    }
]

def capture_screenshot(url):
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--window-size=1200,800')
    
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    driver.get(url)
    screenshot = driver.get_screenshot_as_png()
    driver.quit()
    return screenshot

async def capture_and_send():
    bot = Bot(token=BOT_TOKEN)
    for item in PAGES:
        url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/htmlembed?sheet={item['sheet_name']}&range={item['range']}"
        image_bytes = await asyncio.to_thread(capture_screenshot, url)
        
        photo = BufferedInputFile(image_bytes, filename="report.png")
        await bot.send_photo(chat_id=item["chat_id"], photo=photo, caption=item["caption"])
        
    await bot.session.close()

scheduler = AsyncIOScheduler(timezone="Asia/Tashkent")
scheduler.add_job(capture_and_send, 'cron', hour=21, minute=0)

async def main():
    scheduler.start()
    print("Bot tayyor va 21:00 ni kutmoqda...")
    while True:
        await asyncio.sleep(3600)

if __name__ == '__main__':
    asyncio.run(main())
