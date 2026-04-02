import asyncio
import json
import os
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import WebAppInfo, InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from aiohttp import web

# MA'LUMOTLAR
API_TOKEN = '8725164864:AAHN1v3wTmn9e5D8Pp40PR0MvvjKW9UsVyI'
YOUR_URL = 'https://begimqulov017.github.io/my-telegram-app/'
MANAGER_ID = 8114321110

bot = Bot(token=API_TOKEN)
dp = Dispatcher()
user_orders = {}

# --- RENDER UCHUN WEB SERVER ---
async def handle(request):
    return web.Response(text="Bot is running!")

async def start_server():
    app = web.Application()
    app.router.add_get('/', handle)
    runner = web.AppRunner(app)
    await runner.setup()
    # Render portni avtomatik beradi, bo'lmasa 8080 ishlatamiz
    port = int(os.environ.get("PORT", 8080))
    site = web.TCPSite(runner, '0.0.0.0', port)
    await site.start()
# ------------------------------

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    markup = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Menyuni ochish 🍕🍣", web_app=WebAppInfo(url=YOUR_URL))]
    ])
    await message.answer(f"Salom {message.from_user.first_name}! Buyurtma berish uchun tugmani bosing.", reply_markup=markup)

@dp.message(F.web_app_data)
async def web_app_data_handler(message: types.Message):
    data = json.loads(message.web_app_data.data)
    order_text = "".join([f"• {k}: {v} ta\n" for k, v in data['items'].items() if v > 0])
    if not order_text: return
    user_orders[message.from_user.id] = {"items": order_text, "user": message.from_user.full_name}
    kb = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text="📞 Telefon yuborish", request_contact=True)]], resize_keyboard=True)
    await message.answer(f"Savatda:\n{order_text}\nTelefoningizni yuboring:", reply_markup=kb)

@dp.message(F.contact)
async def contact_handler(message: types.Message):
    if message.from_user.id in user_orders:
        user_orders[message.from_user.id]["phone"] = message.contact.phone_number
        kb = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text="📍 Lokatsiya yuborish", request_location=True)]], resize_keyboard=True)
        await message.answer("Lokatsiyangizni yuboring:", reply_markup=kb)

@dp.message(F.location)
async def location_handler(message: types.Message):
    uid = message.from_user.id
    if uid in user_orders:
        order = user_orders[uid]
        await message.answer("Rahmat! Buyurtma yuborildi.", reply_markup=ReplyKeyboardRemove())
        msg = f"🔔 YANGI BUYURTMA!\n👤 {order['user']}\n📞 {order['phone']}\n🛒 {order['items']}"
        await bot.send_message(MANAGER_ID, msg)
        await bot.send_location(MANAGER_ID, message.location.latitude, message.location.longitude)
        del user_orders[uid]

async def main():
    asyncio.create_task(start_server())
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
