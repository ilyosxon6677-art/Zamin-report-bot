import asyncio
from aiogram import Bot
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from playwright.async_api import async_playwright
from aiogram.types import BufferedInputFile

# --- BOT VA GURUHLAR SOZLAMALARI ---
# BotFather bergan TOKEN kodingizni qo'shtirnoq ichiga yozing:
BOT_TOKEN = "SIZNING_BOT_TOKENINGIZ"

# Guruh ID raqamlari
CHAT_ID_48 = -1002717046752
CHAT_ID_34 = -1004397692925
# CHAT_ID_ZAMIN = -100XXXXXXXXXX  # Zamin Teks guruhi ID'si tayyor bo'lgach qo'shiladi

SHEET_ID = "1xBro7Q_Bn-FnABrvTQQooL_2fSoxobMi"

# Yuboriladigan sahifalar va diapazonlar
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

async def capture_and_send():
    bot = Bot(token=BOT_TOKEN)
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        
        for item in PAGES:
            # Google Sheets'dan kerakli qismini HTML ko'rinishida olib rasmga tushirish
            url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/htmlembed?sheet={item['sheet_name']}&range={item['range']}"
            await page.goto(url)
            await page.set_viewport_size({"width": 1200, "height": 800})
            
            image_bytes = await page.screenshot(full_page=True)
            
            # Telegram guruhiga yuborish
            photo = BufferedInputFile(image_bytes, filename="report.png")
            await bot.send_photo(chat_id=item["chat_id"], photo=photo, caption=item["caption"])
            
        await browser.close()
    await bot.session.close()

# Toshkent vaqti bilan har kuni soat 21:00 da avtomatik ishlaydi
scheduler = AsyncIOScheduler(timezone="Asia/Tashkent")
scheduler.add_job(capture_and_send, 'cron', hour=21, minute=0)

async def main():
    scheduler.start()
    print("Bot muvaffaqiyatli ishga tushdi va har kuni 21:00 da hisobot yuborishga tayyor.")
    while True:
        await asyncio.sleep(3600)

if __name__ == '__main__':
    asyncio.run(main())
