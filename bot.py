import os
import asyncio
from http.server import HTTPServer, BaseHTTPRequestHandler
import threading
import urllib.request
from aiogram import Bot, Dispatcher
from aiogram.filters import Command
from aiogram.types import BufferedInputFile, Message
from apscheduler.schedulers.asyncio import AsyncIOScheduler

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

# YANGI GOOGLE SHEETS ID
SHEET_ID = "1lxkukZc2Th38J-Wq6-Fd38fK-ndksBD7TaidajfzVw4"

PAGES = [
    {
        "chat_id": CHAT_ID_48,
        "sheet_name": "Stanoklar bo'yicha",
        "caption": "📊 Kunlik Stanoklar hisoboti"
    },
    {
        "chat_id": CHAT_ID_34,
        "sheet_name": "Kunlik krim 34",
        "caption": "📊 Kunlik Krim (34) hisoboti"
    }
]

dp = Dispatcher()

def fetch_sheet_pdf(sheet_name):
    encoded_name = urllib.parse.quote(sheet_name)
    url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=pdf&portrait=false&size=A4&fitw=true&gridlines=true&sheet={encoded_name}"
    
    req = urllib.request.Request(
        url, 
        headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
    )
    with urllib.request.urlopen(req) as response:
        return response.read()

async def capture_and_send():
    bot = Bot(token=BOT_TOKEN)
    for item in PAGES:
        pdf_bytes = await asyncio.to_thread(fetch_sheet_pdf, item['sheet_name'])
        
        document = BufferedInputFile(pdf_bytes, filename=f"{item['sheet_name']}.pdf")
        await bot.send_document(chat_id=item["chat_id"], document=document, caption=item["caption"])
        
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
