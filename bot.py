import os
import asyncio
from http.server import HTTPServer, BaseHTTPRequestHandler
import threading
from aiogram import Bot, Dispatcher
from aiogram.filters import Command
from aiogram.types import BufferedInputFile, Message
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from playwright.async_api import async_playwright

# --- RENDER UCHUN DUMMY SERVER ---
class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot ishlayapti!")

def run_dummy_server():
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(('0.0.0.0', port), SimpleHTTPRequestHandler)
    server.serve_forever()

# --- BOT SOZLAMALARI ---
BOT_TOKEN = "8704184895:AAEKbSKQcAgMNtOML1ecWHVjfd4ecBsIY3o"

CHAT_ID_48 = -1002717046752
CHAT_ID_34 = -1004397692925

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

dp = Dispatcher()

async def capture_screenshot(url):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page(viewport={"width": 1200, "height": 800})
        await page.goto(url)
        await page.wait_for_timeout(3000)  # Jadval yuklanishi uchun 3 soniya kutadi
        screenshot = await page.screenshot(type="png")
        await browser.close()
        return screenshot

async def capture_and_send():
    bot = Bot(token=BOT_TOKEN)
    for item in PAGES:
        url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/htmlembed?sheet={item['sheet_name']}&range={item['range']}"
        image_bytes = await capture_screenshot(url)
        
        photo = BufferedInputFile(image_bytes, filename="report.png")
        await bot.send_photo(chat_id=item["chat_id"], photo=photo, caption=item["caption"])
        
    await bot.session.close()

@dp.message(Command("start"))
async def cmd_start(message: Message):
    await message.answer("Salom! Bot ishlayapti. Hisobotlarni zudlik bilan yuborish uchun /send buyrug'ini yuboring.")

@dp.message(Command("send"))
async def cmd_send(message: Message):
    await message.answer("Hisobotlar tayyorlanmoqda va guruhlarga yuborilmoqda...")
    try:
        await capture_and_send()
        await message.answer("Hisobotlar muvaffaqiyatli yuborildi!")
    except Exception as e:
        await message.answer(f"Xatolik yuz berdi: {e}")

scheduler = AsyncIOScheduler(timezone="Asia/Tashkent")
scheduler.add_job(capture_and_send, 'cron', hour=21, minute=0)

async def main():
    threading.Thread(target=run_dummy_server, daemon=True).start()
    scheduler.start()
    bot = Bot(token=BOT_TOKEN)
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
