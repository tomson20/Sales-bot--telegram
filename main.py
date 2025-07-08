import os
import json
import logging

from fastapi import FastAPI, Request
import uvicorn

from aiogram import Bot, Dispatcher, types
from aiogram.utils.exceptions import BotBlocked, ChatNotFound, TelegramAPIError

import gspread
from config import BOT_TOKEN, ADMIN_CHAT_ID, SPREADSHEET_ID, WEBHOOK_URL

# === Logging ===
logging.basicConfig(level=logging.INFO)

# === Initialize FastAPI ===
app = FastAPI()

# === Initialize bot ===
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)

# === Google Sheets setup ===
gc = gspread.service_account(filename="credentials.json")
sh = gc.open_by_key(SPREADSHEET_ID)
worksheet = sh.sheet1

# === Sample products ===
products = {
    "1": "შეკვეთის მიმღები AI-ბოტი - 400₾",
    "2": "ჯავშნის მიმღები AI-ბოტი - 400₾",
    "3": "პირადი AI-აგენტი - 400₾",
    "4": "ინვოისების და გადახდის გადაგზავნის AI-ბოტი - 400₾",
    "5": "თქვენზე მორგებული AI-ბოტების შექმნა - შეთანხმებით",
    "6": "ავტომატიზირებული სისტემების შექმნა AI გამოყენებით - შეთანხმებით",
    "7": "ვებგვერდების და აპლიკაციების შემოწმება უსაფრთხოებაზე - შეთანხმებით"
}

user_data = {}

# === Routes ===
@app.get("/")
async def root():
    return {"status": "🤖 Bot is running with webhook on Render"}

@app.post("/webhook")
async def telegram_webhook(request: Request):
    body = await request.body()
    logging.info(f"📩 მიღებულია update: {body}")

    update = types.Update(**json.loads(body))
    await dp.process_update(update)

    return {"ok": True}


# === Bot Handlers ===
@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    await message.reply("გამარჯობა! აირჩიე პროდუქტი ნომრის მიხედვით:\n" + "\n".join([f"{k}. {v}" for k, v in products.items()]))

@dp.message_handler(lambda message: message.text in products.keys())
async def product_selected(message: types.Message):
    user_data[message.from_user.id] = {"product": products[message.text]}
    await message.reply("შენ აირჩიე: " + products[message.text])
    await message.reply("შეიყვანეთ თქვენი სახელი:")

@dp.message_handler(lambda message: message.from_user.id in user_data and "name" not in user_data[message.from_user.id])
async def get_name(message: types.Message):
    user_data[message.from_user.id]["name"] = message.text
    await message.reply("შეიყვანეთ მისამართი:")

@dp.message_handler(lambda message: message.from_user.id in user_data and "address" not in user_data[message.from_user.id])
async def get_address(message: types.Message):
    user_data[message.from_user.id]["address"] = message.text
    await message.reply("შეიყვანეთ ტელეფონი:")

@dp.message_handler(lambda message: message.from_user.id in user_data and "phone" not in user_data[message.from_user.id])
async def get_phone(message: types.Message):
    user_data[message.from_user.id]["phone"] = message.text

    data = user_data[message.from_user.id]
    worksheet.append_row([
        message.from_user.username or str(message.from_user.id),
        data["product"],
        data["name"],
        data["address"],
        data["phone"]
    ])

    try:
        await bot.send_message(
            ADMIN_CHAT_ID,
            f"📥 ახალი შეკვეთა:\n"
            f"👤 მომხმარებელი: {message.from_user.username or message.from_user.id}\n"
            f"📦 პროდუქტი: {data['product']}\n"
            f"📛 სახელი: {data['name']}\n"
            f"📍 მისამართი: {data['address']}\n"
            f"📞 ტელეფონი: {data['phone']}"
        )
    except BotBlocked:
        logging.warning(f"ბოტი დაბლოკილია ADMIN_CHAT_ID: {ADMIN_CHAT_ID}")
    except ChatNotFound:
        logging.warning(f"ჩეთი ვერ მოიძებნა: {ADMIN_CHAT_ID}")
    except TelegramAPIError as e:
        logging.error(f"Telegram API შეცდომა: {e}")

    await message.reply("გმადლობთ! თქვენი შეკვეთა მიღებულია ✅")
    del user_data[message.from_user.id]

# === Start server & webhook setup ===
if __name__ == "__main__":
    import asyncio

    async def startup():
        await bot.set_webhook(WEBHOOK_URL)
        logging.info(f"✅ Webhook დაყენებულია: {WEBHOOK_URL}")

    async def shutdown():
        logging.info("❌ Webhook იშლება...")
        await bot.delete_webhook()

    asyncio.run(startup())

    port = int(os.environ.get("PORT", 10000))  # Render პორტი
    uvicorn.run("main:app", host="0.0.0.0", port=port)
