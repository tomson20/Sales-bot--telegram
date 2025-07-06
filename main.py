from aiogram import Bot, Dispatcher, types
from aiogram.types import ParseMode
from aiogram.utils import executor
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
import gspread
import os
from config import BOT_TOKEN, ADMIN_CHAT_ID, SPREADSHEET_ID # შესაძლებელია ასევე დაამატო გადახდის მეთოდი.

# Initialize bot
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)

# Google Sheets setup
gc = gspread.service_account(filename="credentials.json")
sh = gc.open_by_key(SPREADSHEET_ID)
worksheet = sh.sheet1

# Sample products
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

@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    await message.reply("გამარჯობა! აირჩიე პროდუქტი:\n" + "\n".join([f"{k}. {v}" for k, v in products.items()]))

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

    # Save to Google Sheet
    data = user_data[message.from_user.id]
    worksheet.append_row([
        message.from_user.username or message.from_user.id,
        data["product"],
        data["name"],
        data["address"],
        data["phone"]
    ])

    # Notify admin
    await bot.send_message(
        ADMIN_CHAT_ID,
        f"ახალი შეკვეთა!\n"
        f"მომხმარებელი: {message.from_user.username or message.from_user.id}\n"
        f"პროდუქტი: {data['product']}\n"
        f"სახელი: {data['name']}\n"
        f"მისამართი: {data['address']}\n"
        f"ტელეფონი: {data['phone']}"
    )

    await message.reply("გმადლობთ! თქვენი შეკვეთა მიღებულია!")
    del user_data[message.from_user.id]

if __name__ == '__main__':
    print("Bot is running...")
    executor.start_polling(dp, skip_updates=True)