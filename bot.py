from aiogram import Bot, Dispatcher
from aiogram.filters import Command
from aiogram.types import Message
from config import *
import google.generativeai as genai
import asyncio
import re


bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()
genai.configure(api_key=GEMINI_TOKEN)

chat_model = genai.GenerativeModel(model)

# Создание чата
chat = chat_model.start_chat()

# Вводный промпт
response = chat.send_message(START_PROMPTS["base"])

@dp.message(Command("set_model"))
async def set_model(message: Message):
    global model

    if str(message.from_user.id) in ADMINS:
        get_model = re.search(r"^/set_model\s(.+)", message.text)

        if get_model != None:
            model = get_model.group(1)
            await message.answer("✅ Успешно изменена модель")

        else:
            await message.answer("❗ Пожалуйста укажите модель (/set_model <имя модели>)")

    else:
        await message.answer("❗ У вас нет прав на выполнение команды")


@dp.message(Command("reload"))
async def reload_chat(message: Message):
    global chat
    chat = chat_model.start_chat()
    await message.answer("❗Создан новый чат")
    response = chat.send_message(START_PROMPTS["base"])

@dp.message(Command("start"))
async def start_command(message: Message):
    await message.answer("Привет я FreshAI, могу общатся с вами и развлекать :) А так же мой код скоро будет доступен на github!")

@dp.message(Command("ai"))
async def ai_responce(message: Message):
    try:
        get_prompt = re.search(r"^/ai\s(.+)", message.text)

        if get_prompt != None:
            await message.reply(chat.send_message(get_prompt.group(1)).text, parse_mode="markdown")

        else:
            await message.answer("❗ Пожалуйста пришлите сообщение (/ai <Ваше сообщение>)")
    except Exception as error:
        await message.answer(f"⚙️ Оооп, произошла ошибка, скажите @JustPythonLanguage что бы пофиксил, подробнее:\n\n```\n{error}\n```", parse_mode="markdown")

async def start():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(start())
