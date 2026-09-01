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

# Xabar borishi kerak bo'lgan guruhlar ro'yxati
TARGET_CHATS = [
    -1002717046752,  # 48 tali Tokuv
    -1004397692925   # 34 tali guruh
]

SHEET_ID = "1lxkukZc2Th38J-Wq6-Fd38fK-ndksBD7TaidajfzVw4"

# Faqat siz ko'rsatgan 3 ta varaq
TARGET_SHEETS = [
    {"name": "Stanoklar bo'yicha", "caption": "📊 Stanoklar bo'yicha hisobot"},
    {"name": "Metr Jamlanma va Oylik", "caption": "📊 Metr Jamlanma va Oylik hisoboti"},
    {"name": "Kunlik Tabel", "caption": "📊 Kunlik Tabel hisoboti"}
]

dp = Dispatcher()

def fetch_sheet_image(sheet_name):
    encoded_name = urllib.parse.quote(sheet_name)
    # Google Sheets varag'ini to'g'ridan-to'g'ri PNG rasm qilib yuklash
    url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=png&sheet={encoded_name}"
    
    req = urllib.request.Request(
        url, 
        headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
    )
    with urllib.request.urlopen(req) as response:
        return response.read()

async def capture_and_send():
    bot = Bot(token=BOT_TOKEN)
    
    for sheet in TARGET_SHEETS:
        try:
            # Varaqni rasm holatida olish
            image_bytes = await asyncio.to_thread(fetch_sheet_image, sheet['name'])
            
            # Har bir guruhga rasm sifatida yuborish
            for chat_id in TARGET_CHATS:
                photo = BufferedInputFile(image_bytes, filename=f"{sheet['name']}.png")
                await bot.send_photo(chat_id=chat_id, photo=photo, caption=sheet['caption'])
                await asyncio.sleep(1)
        except Exception as e:
            print(f"Xatolik ({sheet['name']}): {e}")
            
    await bot.session.close()

@dp.message(Command("start"))
async def cmd_start(message: Message):
    await message.answer("Salom! Bot ishlayapti. Hisobotlarni zudlik bilan yuborish uchun /send buyrug'ini yuboring.")

@dp.message(Command("send"))
async def cmd_send(message: Message):
    await message.answer("Hisobotlar tayyorlanmoqda va guruhlarga yuborilmoqda...")
    try:
        await capture_and_send()
        await message.answer("Barcha 3 ta hisobot rasmlari guruhlarga yuborildi!")
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
