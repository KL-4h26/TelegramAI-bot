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

model = genai.GenerativeModel(MODEL)

# Создание чата
chat = model.start_chat()

# Вводный промпт
response = chat.send_message(START_PROMPTS["base"])

@dp.message(Command("reload"))
async def reload_chat(message: Message):
    global chat
    chat = model.start_chat()
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
            await message.reply(chat.send_message(get_prompt.group(1)).text)

        else:
            await message.answer("❗ Пожалуйста пришлите сообщение (/ai <Ваше сообщение>)")
    except:
        await message.answer("⚙️ Оооп, произошла ошибка, скажите @JustPythonLanguage что бы посмотрел в логах че произошло и исправил")

async def start():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(start())