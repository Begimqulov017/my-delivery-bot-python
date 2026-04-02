import asyncio
import json
import os
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import (
    WebAppInfo, 
    InlineKeyboardMarkup, 
    InlineKeyboardButton, 
    ReplyKeyboardMarkup, 
    KeyboardButton, 
    ReplyKeyboardRemove
)
from aiohttp import web

# MA'LUMOTLAR - O'zgartirmang!
API_TOKEN = '8725164864:AAHN1v3wTmn9e5D8Pp40PR0MvvjKW9UsVyI'
YOUR_URL = 'https://begimqulov017.github.io/my-telegram-app/'
MANAGER_ID = 5774691559

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
    port = int(os.environ.get("PORT", 8080))
    site = web.TCPSite(runner, '0.0.0.0', port)
    await site.start()
# ------------------------------

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    markup = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Menyuni ochish 🍕🍣", web_app=WebAppInfo(url=YOUR_URL))]
    ])
    await message.answer(
        f"Salom {message.from_user.first_name}!\nBuyurtma berish uchun pastdagi tugmani bosing:",
        reply_markup=markup
    )

@dp.message(F.web_app_data)
async def web_app_data_handler(message: types.Message):
    try:
        data = json.loads(message.web_app_data.data)
        order_text = ""
        for item, count in data['items'].items():
            if count > 0:
                order_text += f"• {item}: {count} ta\n"
        
        if not order_text:
            await message.answer("Savat bo'sh!")
            return

        # Ma'lumotlarni vaqtincha saqlash
        user_orders[message.from_user.id] = {
            "items": order_text,
            "name": message.from_user.full_name,
            "username": f"@{message.from_user.username}" if message.from_user.username else "Mavjud emas"
        }

        kb = ReplyKeyboardMarkup(keyboard=[
            [KeyboardButton(text="📞 Telefon raqamni yuborish", request_contact=True)]
        ], resize_keyboard=True, one_time_keyboard=True)
        
        await message.answer(f"Sizning tanlovingiz:\n{order_text}\nEndi telefon raqamingizni yuboring:", reply_markup=kb)
    except Exception as e:
        print(f"Xato yuz berdi: {e}")

@dp.message(F.contact)
async def contact_handler(message: types.Message):
    uid = message.from_user.id
    if uid in user_orders:
        user_orders[uid]["phone"] = message.contact.phone_number
        
        kb = ReplyKeyboardMarkup(keyboard=[
            [KeyboardButton(text="📍 Lokatsiyani yuborish", request_location=True)]
        ], resize_keyboard=True, one_time_keyboard=True)
        
        await message.answer("Rahmat! Endi lokatsiyangizni yuboring:", reply_markup=kb)

@dp.message(F.location)
async def location_handler(message: types.Message):
    uid = message.from_user.id
    if uid in user_orders:
        order = user_orders[uid]
        
        # 1. Mijozga tasdiq
        await message.answer("Rahmat! Buyurtma qabul qilindi. Operator siz bilan bog'lanadi.", reply_markup=ReplyKeyboardRemove())

        # 2. MANAGERGA YUBORISH (ASOSIY QISM)
        manager_msg = (
            f"🔔 YANGI BUYURTMA!\n\n"
            f"👤 Mijoz: {order['name']} ({order['username']})\n"
            f"📞 Tel: {order['phone']}\n\n"
            f"🛒 Savat:\n{order['items']}"
        )
        
        try:
            await bot.send_message(MANAGER_ID, manager_msg)
            await bot.send_location(MANAGER_ID, message.location.latitude, message.location.longitude)
        except Exception as e:
            print(f"Managerga yuborishda xato: {e}")
            # Agar manager ID botni start qilmagan bo'lsa, xato beradi
        
        del user_orders[uid]

async def main():
    asyncio.create_task(start_server())
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
