from os import getenv
import asyncio
import os
from aiogram import Bot, Dispatcher, Router, F
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from aiogram.filters import CommandStart
from dotenv import load_dotenv

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), ".env"))
TOKEN = getenv("BOT_TOKEN")

if not TOKEN:
    raise ValueError("BOT_TOKEN не найден! Проверь файл .env")

dp = Dispatcher()
router = Router()
dp.include_router(router)

ADMIN_ID = 1355583869   # ← сюда вставь свой Telegram ID

def get_main_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🎶 навигация"), KeyboardButton(text="🎶 позвать admина")],
            [KeyboardButton(text="🎶 стать админом")],
            [KeyboardButton(text="🎶 правила")],
        ],
        resize_keyboard=True,
        one_time_keyboard=False
    )

@router.message(CommandStart())
async def start(message: Message):
    await message.answer_photo(
        photo="https://i.imgur.com/xxxxxx.jpg",  # ← ссылка на фото или file_id
        caption=(
            ". * рады приветствовать тебя в нашем омуте!🌿\n"
            "чтобы тебе предоставили администратора, нужно всего лишь поздороваться;)\n\n"
            "🔗 важные ссылки:\n"
            "@quietomut — тгк\n"
            "@quietomuto — отзывы\n"
            "@technicalsupportomut_bot — тех.поддержка"
        ),
        reply_markup=get_main_keyboard()
    )

@router.message(F.text == "🎶 навигация")
async def navigation(message: Message):
    await message.answer(
        "🗺 навигация:\n\n"
        "@quietomut — основной канал\n"
        "@quietomuto — отзывы\n"
        "@technicalsupportomut_bot — тех.поддержка"
    )

@router.message(F.text == "🎶 позвать admина")
async def call_admin(message: Message, bot: Bot):
    user = message.from_user
    await bot.send_message(
        ADMIN_ID,
        f"❗ пользователь зовёт админа!\n"
        f"👤 {user.full_name}\n"
        f"🔗 @{user.username or 'нет username'}\n"
        f"🆔 {user.id}"
    )
    await message.answer("✅ админ скоро подойдёт, подожди немного~")

@router.message(F.text == "🎶 стать админом")
async def become_admin(message: Message):
    await message.answer(
        "📋 чтобы стать админом:\n\n"
        "напиши нам и расскажи о себе.\n"
        "мы рассмотрим твою кандидатуру~"
    )

@router.message(F.text == "🎶 правила")
async def rules(message: Message):
    await message.answer(
        "📜 правила омута:\n\n"
        "1. уважай других\n"
        "2. не флудить\n"
        "3. не спамить\n"
        "4. слушаться администрацию\n\n"
        "нарушение правил = бан 🌊"
    )

async def main():
    bot = Bot(token=TOKEN)
    await bot.delete_webhook(drop_pending_updates=True)
    print("Bot is starting...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())