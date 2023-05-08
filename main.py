from gpt import *
import logging
from decouple import config
import time
from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import ParseMode
from database.database import *
import os

import json

BOT_TOKEN = config("TELEGRAM_BOT_TOKEN")
bot = Bot(BOT_TOKEN)
dp = Dispatcher(bot)
# Включаем логирование, чтобы не пропустить важные сообщения
logging.basicConfig(level=logging.INFO)

active_requests_id = set()


@dp.message_handler(commands=['start'])
async def start(message):
    if not is_user_exists(message.from_user.id):
        add_user(
            name=message.from_user.first_name,
            username=message.from_user.username,
            telegram_id=message.from_user.id
        )

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(types.KeyboardButton("/reset_conversation"))
    init_conversation()
    await message.answer(
        f"Привет, {message.from_user.first_name}. Это ChatGPT бот. Можете задавать интересующий вас вопрос чат.",
        reply_markup=markup)


def rate_limit_error_handler(func):
    """
        Декоратор ,отслеживающий ошибку RateLimitError и повторяет запросы с периодом retry_after
    """

    async def wrapper_func(message):
        try:
            await func(message)
        except openai.error.RateLimitError as e:
            delete_last_el()
            retry_time = e.retry_after if hasattr(e, 'retry_after') else 5
            await message.answer(f"Превышен лимит запросов. Ждёмс... :)")
            time.sleep(retry_time)
            return await wrapper_func(message)

    return wrapper_func


def recurrent_request_handler(func):
    """
        Декоратор, отслеживающий одновременно два+ запроса и предотвращающий это
    """

    async def wrapper_func(message):
        global active_requests_id
        if message.from_user.id in active_requests_id:
            await message.answer(f"Запрос уже отправлен. Ждём ответа")
            return wrapper_func
        active_requests_id.add(message.from_user.id)
        await func(message)
        active_requests_id.discard(message.from_user.id)

    return wrapper_func


@dp.message_handler(commands=['reset_conversation'])
@recurrent_request_handler
@rate_limit_error_handler
async def reset_conversation(message):
    init_conversation()
    increment_number_of_requests(message.from_user.id)
    await message.answer(f"Диалог сброшен. Чем я могу помочь?")


@dp.message_handler(commands=['admin'])
@recurrent_request_handler
@rate_limit_error_handler
async def admin(message):
    if message.from_user.username == 'yurchest':
        data = get_all_users()
        json_data = json.dumps(data, indent=2, ensure_ascii=False)
        await message.answer(f"```\n{json_data}```", parse_mode=ParseMode.MARKDOWN)
    else:
        await message.answer("Вы не админ")


@dp.message_handler()
@recurrent_request_handler
@rate_limit_error_handler
async def main(message):
    response = chatgpt_conversation(message.text)
    increment_number_of_requests(message.from_user.id)
    await message.answer(response)


if __name__ == "__main__":
    # Запуск бота
    executor.start_polling(dp, skip_updates=True)
