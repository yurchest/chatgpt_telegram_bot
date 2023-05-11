from gpt import *

import logging
from decouple import config
import asyncio
from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import ParseMode
from database.database import *
import os

import json

BOT_TOKEN = config("TELEGRAM_BOT_TOKEN")
YOOKASSA_PAYMENT_TOKEN = config("YOOKASSA_PAYMENT_TOKEN")
bot = Bot(BOT_TOKEN)
dp = Dispatcher(bot)
# Включаем логирование, чтобы не пропустить важные сообщения
logging.basicConfig(level=logging.INFO)

active_requests_id = set()
active_msg_response = dict()


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
            # await message.answer(f"Превышен лимит запросов. Ждёмс... :)")
            await asyncio.sleep(retry_time)
            return await wrapper_func(message)

    return wrapper_func


def recurrent_request_handler(func):
    """
        Декоратор, отслеживающий одновременно два+ запроса и предотвращающий это
    """

    async def wrapper_func(message):
        global active_requests_id
        if message.from_user.id in active_requests_id:
            await message.answer(f"Не так быстро. Повторите запрос.")
            return wrapper_func
        active_requests_id.add(message.from_user.id)
        await func(message)
        active_requests_id.discard(message.from_user.id)

    return wrapper_func


def main_handler(func):
    """
        Декоратор общей функциональности
    """

    async def wrapper_func(message: types.message):
        if not is_user_exists(message.from_user.id):
            await message.answer(
                f"Привет, {message.from_user.first_name}! Я рад тебя видеть здесь! Я - чат-бот, созданный на базе GPT. Я могу помочь тебе в различных задачах и ответить на любые вопросы. Просто напиши мне, что ты хочешь узнать! \n У тебя есть тестовый режим на 50 запросов. Удачи!")
            add_user(
                name=message.from_user.first_name,
                username=message.from_user.username,
                telegram_id=message.from_user.id
            )
            await message.answer(f"Чтобы получить полный доступ к боту, поблагодари разработчика монетой :)")
            await pay(message)
        if not is_user_test_period(message.from_user.id):
            if not is_user_paid(message.from_user.id):
                await message.answer(f"Чтобы получить полный доступ к боту, поблагодари разработчика монетой :)")
                await pay(message)
                return
        increment_number_of_requests(message.from_user.id)
        await func(message)

    return wrapper_func


def dots_handler(func):
    """
        Декоратор для . . . . . .
    """

    async def wrapper_func(message: types.message):
        global active_msg_response
        if message.message_id not in active_msg_response:
            msg = await message.answer(". . . . . . . . .")
            active_msg_response.update({message.message_id: msg.message_id})
        await func(message)
        active_msg_response.pop(message.message_id)

    return wrapper_func


@dp.message_handler(commands=['start'])
@main_handler
async def start(message: types.message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(types.KeyboardButton("/reset_conversation"))
    markup.add(types.KeyboardButton("/help"))
    if message.from_user.username == 'yurchest':
        markup.add(types.KeyboardButton("/admin"))
    init_conversation()
    await message.answer(
        "Можете задавать интересующий вас вопрос чат.",
        reply_markup=markup)


@dp.message_handler(commands=['help'])
async def start(message: types.message):
    await message.answer(
        "Телеграм бот предназнчен для легкого взаимодействия с OpenAI API (ChatGPT).\n\
У пользователя есть 50 бесплатных пробных запросов для знакомства с сервисом. \n\
Чтобы получить неограниченное число запросов, необходимо оплатить подписку (на данный момент 100 руб.). \n\
Также присутствует кнопка меню '/reset_conversation', сбрасывающая историю сообщений (необходимо, \
eсли пользователь хочет поменять тему диалога).\n\
Данные пользователя хранятся в базе даных на выделенном сервере.")


@dp.message_handler(commands=['pay'])
async def pay(message: types.message):
    if is_user_paid(message.from_user.id):
        await message.answer(
            "У вас уже есть полный доступ. Но если вы хотите заплатить еще денюжку, то я всегда рад (^_^)")
    await bot.send_invoice(
        chat_id=message.chat.id,
        title="Оплата подписки",
        description="Оплата подписки Yurchest BOT",
        payload="invoice",
        start_parameter="paymanet",
        provider_token=YOOKASSA_PAYMENT_TOKEN,
        currency="RUB",
        prices=[types.LabeledPrice(label="Оплата подписки", amount=100 * 100)],
        provider_data={
            "receipt": {
                "items": [
                    {
                        "description": "Подписка на Yurchest Chat Bot",
                        "quantity": "1.00",
                        "amount":
                            {
                                "value": "100.00",
                                "currency": "RUB",
                            },
                        "vat_code": 1,
                    }],
                "customer":
                    {
                        "email": "yurchest@gmail.com",
                    }
            }
        }
    )


# pre checkout  (must be answered in 10 seconds)
@dp.pre_checkout_query_handler(lambda query: True)
async def pre_checkout_query(pre_checkout_q: types.PreCheckoutQuery):
    print("xxx")
    await bot.answer_pre_checkout_query(pre_checkout_q.id, ok=True)


@dp.message_handler(content_types=types.ContentType.SUCCESSFUL_PAYMENT)
async def success_payment(message: types.message):
    await message.answer(f"Успешно оплачено: \n{message.succesful_payment.order_info}")


@dp.message_handler(commands=['reset_conversation'])
@dots_handler
@main_handler
@recurrent_request_handler
@rate_limit_error_handler
async def reset_conversation(message):
    init_conversation()
    await bot.edit_message_text(chat_id=message.chat.id, message_id=active_msg_response[message.message_id],
                                text=f"Диалог сброшен. Чем я могу помочь?")


@dp.message_handler(commands=['admin'])
@dots_handler
@recurrent_request_handler
@rate_limit_error_handler
async def admin(message: types.message):
    if message.from_user.username == 'yurchest':
        data = get_all_users()
        json_data = json.dumps(data, indent=2, ensure_ascii=False)
        await bot.edit_message_text(chat_id=message.chat.id, message_id=active_msg_response[message.message_id],
                                    text=f"```\n{json_data}```", parse_mode=ParseMode.MARKDOWN)
    else:
        await bot.edit_message_text(chat_id=message.chat.id, message_id=active_msg_response[message.message_id],
                                    text="Вы не админ")


@dp.message_handler()
@dots_handler
@main_handler
# @recurrent_request_handler
@rate_limit_error_handler
async def main(message: types.message, retry=False):
    response = chatgpt_conversation(message.text)
    await bot.edit_message_text(chat_id=message.chat.id, message_id=active_msg_response[message.message_id],
                                text=response)


if __name__ == "__main__":
    # Запуск бота
    executor.start_polling(dp, skip_updates=True)
