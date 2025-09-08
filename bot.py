from aiogram import Bot, Dispatcher, exceptions, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from config import *
import httpx
from openai import OpenAI
import asyncio
import re

# START_PROMPTS
disable = False

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()
client = OpenAI(
    base_url="https://api.onlysq.ru/ai/openai",
    api_key=OPENAI_TOKEN,
)

# Создание чата
# chat = chat_model.start_chat()

# Вводный промпт
# response = chat.send_message(START_PROMPTS["base"])

# Чаты
chats = {

}


def user_chat(user_id: int, username: str):
    global chats

    if user_id in chats:
        return chats[user_id]
    
    chats[user_id] = [{"role": "system", "content": START_PROMPTS["base"](user=username)}]

    return chats[user_id]
    


@dp.message(Command("disable"))
async def disable_command(message: Message):
    global disable

    # Проверка на админа
    if message.from_user.id in ADMINS:    
        # Перевод в состояние
        disable = True if not disable else False

        # Уведомление
        await message.answer(f'✅ Бот переведен в состояние: {"спящий" if disable else "работающий"}')
        return
    
    await message.answer("❗ У вас нет прав на выполнение команды")
        

@dp.message(Command("set_model"))
async def set_model(message: Message):
    global model

    # Проверка на админа
    if message.from_user.id in ADMINS:

        async with httpx.AsyncClient() as client:
            response = await client.get("https://api.onlysq.ru/ai/models")
            response.raise_for_status()
            response = response.json()["models"]

        temp = []

        models = InlineKeyboardMarkup(inline_keyboard=[
            
        ])

        for m in response.keys():
            if len(temp) == 2:
                models.inline_keyboard.append(temp)
                temp = []
                continue

            temp.append(InlineKeyboardButton(text=m, callback_data=f"setmodel {m}"))


        await message.answer("Доступные модели:", reply_markup=models)
        return


    await message.answer("❗ У вас нет прав на выполнение команды")
        

@dp.message(Command("reload"))
async def reload_chat(message: Message):
    global chats

    # Создание нового чата
    chats[message.from_user.id] = [{"role": "system", "content": START_PROMPTS["base"](user=message.from_user.username)}]

    # Уведомление
    await message.answer("❗Создан новый чат")

@dp.message(Command("global_reload"))
async def gobal_reload_command(message: Message):
    global chats

    # Проверка на админа
    if message.from_user.id in ADMINS:
        # await message.answer(str(chats))
        chats = {

        }
        await message.answer("✅ Все чаты успешно очищены")
        return
    
    await message.answer("❗ У вас нет прав на выполнение команды")


@dp.message(Command("start"))
async def start_command(message: Message):
    if disable:
        return
    
    await message.answer("Привет я FreshAI, могу общатся с вами и развлекать :) А так же мой код скоро будет доступен на github!")

@dp.message(Command("ai"))
async def ai_responce(message: Message):
    if disable:
        return
    
    # Создаем чат если еще не создан
    user_chat(message.from_user.id, message.from_user.username)

    # Парсинг сообщения
    get_prompt = re.search(r"^/ai\s(.+)", message.text)

    # Проверка
    if get_prompt == None:
        await message.answer("❗ Пожалуйста пришлите сообщение (/ai <Ваше сообщение>)")
        return


    chats[message.from_user.id].append({"role": "user", "content": get_prompt.group(1)})
  
    # print(chats[message.from_user.id])
    # Ответ chat
    try:
        completion = client.chat.completions.create(
            model=model,
            messages=user_chat(message.from_user.id, message.from_user.username)
        )

        await message.reply(completion.choices[0].message.content, parse_mode="markdown")

    except exceptions.TelegramBadRequest as error:
        # Проверяем что это конкретно ошибка форматирования
        if "can't parse entities" in str(error):
            # Отправляем без markdown
            await message.reply(completion.choices[0].message.content)
            return
        
        # Если ошибка не в markdown
        await message.answer(f"⚙️ Оооп, произошла ошибка, скажите @JustPythonLanguage что бы пофиксил, подробнее:\n\n```\n{error}\n```", parse_mode="markdown")

    except Exception as error:
        # Сообщение об ошибке
        await message.answer(f"⚙️ Оооп, произошла ошибка, скажите @JustPythonLanguage что бы пофиксил, подробнее:\n\n```\n{error}\n```", parse_mode="markdown")

    if len(chats[message.from_user.id]) >= MAX_CHAT_LENGHT:
        chats[message.from_user.id] = [{"role": "system", "content": START_PROMPTS["base"](user=message.from_user.username)}]
    

@dp.callback_query(F.data.startswith("setmodel"))
async def set_model(clbq: CallbackQuery):

    if clbq.from_user.id in ADMINS:
        global model

        model = clbq.data.split()[1]
        await clbq.message.edit_text("⚙️ Модель успешно изменена")
        return
    
    clbq.answer("Неа")


async def start():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(start())
