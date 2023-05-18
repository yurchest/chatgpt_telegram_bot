from gpt import *
from config import *
import aiogram
import logging
import asyncio
from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import ParseMode
from database import *
from aiogram.dispatcher import FSMContext
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import StatesGroup, State

import json

bot = Bot(BOT_TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())

# Включаем логирование, чтобы не пропустить важные сообщения
logging.basicConfig(level=logging.INFO)

active_requests_id = set()
active_msg_response = dict()


class UserState(StatesGroup):
    some_state = State()


def error_handler(func):
    """
        Декоратор ,обрабатывающий исключения
    """

    async def wrapper_func(message, state):
        try:
            await func(message, state)
        except openai.error.RateLimitError as e:
            # delete_last_el()
            retry_time = e.retry_after if hasattr(e, 'retry_after') else 5
            # await message.answer(f"Превышен лимит запросов. Ждёмс... :)")
            await asyncio.sleep(retry_time)
            return await wrapper_func(message, state)
        except openai.error.InvalidRequestError as e:
            # await message.answer(f"Получился слишком длинный диалог. Попробуйте уменьшить запрос или сбросьте диалог коммандой /reset_conversation")
            await bot.edit_message_text(chat_id=message.chat.id, message_id=active_msg_response[message.message_id],
                                        text=f"Получился слишком длинный диалог. Попробуйте уменьшить запрос или сбросьте диалог коммандой /reset_conversation")
        except Exception as ex:
            await bot.edit_message_text(chat_id=message.chat.id, message_id=active_msg_response[message.message_id],
                                        text=f"Произошла непредвиденная ошибка. Сообщите @yurchest или попробуйте повторить запрос.\n\n {ex}")
            add_error_to_db(str(ex), message.from_user.id)

    return wrapper_func


def recurrent_request_handler(func):
    """
        Декоратор, отслеживающий одновременно два+ запроса и предотвращающий это
    """

    async def wrapper_func(message, state):
        global active_requests_id
        if message.from_user.id in active_requests_id:
            await message.answer(f"Не так быстро. Повторите запрос.")
            return wrapper_func
        active_requests_id.add(message.from_user.id)
        await func(message, state)
        active_requests_id.discard(message.from_user.id)

    return wrapper_func


def main_handler(func):
    """
        Декоратор общей функциональности
    """

    async def wrapper_func(message: types.message, state):
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
        await func(message, state)

    return wrapper_func


def dots_handler(func):
    """
        Декоратор для . . . . . .
    """

    async def wrapper_func(message: types.message, state):
        global active_msg_response
        if message.message_id not in active_msg_response:
            msg = await message.answer(". . . . . . . . .")
            active_msg_response.update({message.message_id: msg.message_id})
        await func(message, state)
        active_msg_response.pop(message.message_id)

    return wrapper_func


@dp.message_handler(commands=['start'], state=None)
@main_handler
async def start(message: types.message, state: FSMContext):
    await UserState.some_state.set()
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    # markup.add(types.KeyboardButton("/reset_conversation"))
    # markup.add(types.KeyboardButton("/help"))
    if message.from_user.username == 'yurchest':
        markup.add(types.KeyboardButton("/admin"))

    await message.answer(
        "Можете задавать интересующий вас вопрос чат.",
        reply_markup=markup)


@dp.message_handler(commands=['help'], state=UserState.some_state)
async def help(message: types.message):
    await message.answer(
        "Телеграм бот предназнчен для легкого взаимодействия с OpenAI API (ChatGPT).\n\
У пользователя есть 50 бесплатных пробных запросов для знакомства с сервисом. \n\
Чтобы получить неограниченное число запросов, необходимо оплатить подписку (на данный момент 100 руб.). \n\
Также присутствует кнопка меню '/reset_conversation', сбрасывающая историю сообщений (необходимо, \
eсли пользователь хочет поменять тему диалога).\n\
Данные пользователя хранятся в базе даных на выделенном сервере.\n\
Если что-то не работет пишите мне @yurchest")


@dp.message_handler(commands=['pay'], state=UserState.some_state)
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
@dp.pre_checkout_query_handler(lambda query: True, state=UserState.some_state)
async def pre_checkout_query(pre_checkout_q: types.PreCheckoutQuery):
    await bot.answer_pre_checkout_query(pre_checkout_q.id, ok=True)


@dp.message_handler(content_types=types.ContentType.SUCCESSFUL_PAYMENT, state=UserState.some_state)
async def success_payment(message: types.message):
    set_user_paid(message.from_user.id, message.successful_payment.telegram_payment_charge_id)
    await message.answer(
        f"Успешно оплачено {message.successful_payment.total_amount // 100} {message.successful_payment.currency}! \
\nНомер платежа:\n{message.successful_payment.telegram_payment_charge_id}")


@dp.message_handler(commands=['reset_conversation'], state=UserState.some_state)
@dots_handler
@main_handler
@recurrent_request_handler
@error_handler
async def reset_conversation(message, state: FSMContext):
    # await state.finish()
    # await UserState.some_state.set()
    # response = init_conversation()
    await state.update_data(conversation=[])
    await bot.edit_message_text(chat_id=message.chat.id, message_id=active_msg_response[message.message_id],
                                text=f"Диалог сброшен. Чем я могу помочь?")


@dp.message_handler(commands=['admin'], state=UserState.some_state)
@dots_handler
@recurrent_request_handler
@error_handler
async def admin(message: types.message, state: FSMContext):
    if message.from_user.username == 'yurchest':
        data = get_all_users()
        json_data = json.dumps(data, indent=2, ensure_ascii=False)
        await bot.edit_message_text(chat_id=message.chat.id, message_id=active_msg_response[message.message_id],
                                    text=f"```\n{json_data}```", parse_mode=ParseMode.MARKDOWN)
    else:
        await bot.edit_message_text(chat_id=message.chat.id, message_id=active_msg_response[message.message_id],
                                    text="Вы не админ")


@dp.message_handler(commands=['show_dialog'], state=UserState.some_state)
@dots_handler
@recurrent_request_handler
@error_handler
async def show_dialog(message: types.message, state: FSMContext):
    user_data = await state.get_data()
    user_conversation = user_data.get('conversation')
    if not user_conversation:
        await bot.edit_message_text(chat_id=message.chat.id, message_id=active_msg_response[message.message_id],
                                    text="Диалог пуст")
        return
    await bot.edit_message_text(chat_id=message.chat.id, message_id=active_msg_response[message.message_id],
                                text=f"Весь диалог:", parse_mode=None)
    for message_conversation in user_conversation:
        sender = "Неизветно кто"
        if message_conversation["role"] == "user":
            sender = "Пользователь"
        elif message_conversation["role"] == "assistant":
            sender = "Бот"
        await message.answer(f"{sender}:\n{'-'*30}\n{message_conversation['content']}\n{'-'*30}")
    print(user_conversation)


@dp.message_handler(state=UserState.some_state)
@dots_handler
@main_handler
# @recurrent_request_handler
@error_handler
async def main_state(message: types.message, state: FSMContext):
    user_data = await state.get_data()
    user_conversation = user_data.get('conversation')
    response = chatgpt_conversation(message.text, user_conversation)
    await state.update_data(conversation=response)
    try:
        await bot.edit_message_text(chat_id=message.chat.id, message_id=active_msg_response[message.message_id],
                                    text=response[-1]['content'].strip(), parse_mode=ParseMode.MARKDOWN)
    except aiogram.utils.exceptions.CantParseEntities:
        await bot.edit_message_text(chat_id=message.chat.id, message_id=active_msg_response[message.message_id],
                                    text=response[-1]['content'].strip(), parse_mode=None)


@dp.message_handler()
async def main(message: types.message):
    await UserState.some_state.set()
    await message.answer(
        f"Произошёл перезапуск сервера. Ваш диалог был сброшен :(\nЯ работаю на этой проблемой. \nПридется повторить "
        f"запрос еще раз. Чем я могу помочь?")


if __name__ == "__main__":
    # Запуск бота
    executor.start_polling(dp, skip_updates=True)
