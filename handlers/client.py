import os
import random
from pathlib import Path
from datetime import *

import aiopytesseract

from aiogoogletrans import Translator
from gigachat import *

from database import *
from keyboards import kb_client, buttons_under_answer, back
from payment import *

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message
from bot import bot

router = Router()


class FormState(StatesGroup):
    result = State()
    last_result_for_gpt = State()
    last_result_for_translate = State()
    user_id = State()
    msg_id = State()
    translated_text = State()
    chatgpt_answer = State()


@router.message(Command(commands=["start"]))
async def command_start(message: Message):
    await add_user(message.from_user.id)
    await message.answer(f'Приветствую, {message.from_user.first_name}! 🤖 Отправь мне изображение с текстом, и я с удовольствием помогу его распознать. 📷💬',reply_markup=kb_client, parse_mode="HTML")


@router.message(F.text.lower() == "помощь")
async def information_about_bot(message: Message):
    await add_user(message.from_user.id)
    await message.answer(f"<b>Распознавание текста:</b> Просто отправьте изображение с текстом, и бот автоматически извлечет текст для вас.\n\n<b>Перевод:</b> Бот способен переводить текст с любого языка на русский.\n\n<b>Поиск ответов:</b> Бот постарается найти для вас ответы в текстовой форме.", parse_mode="HTML")


@router.message(F.text.lower() == "профиль")
async def information_about_bot(message: Message):
    day_of_purchase = await get_day_of_purchase(message.from_user.id)
    days = None
    if day_of_purchase is not None:
        days = date.today() - day_of_purchase

    if days is not None and days.days >= 30:
        await end_of_sub(message.from_user.id)

    if day_of_purchase is None:
        data = ' ⛔ '
    else:
        data = day_of_purchase + timedelta(days=30)

    requests = await get_requests(None, message.from_user.id, 'images_sent')
    status = await get_status(message.from_user.id)
    await message.answer(f'📊 <b>Ваш профиль:</b>\n\n<b>Имя</b> - {message.from_user.first_name}\n<b>Айди</b> - {message.from_user.id}\n<b>Ваши запросы</b> - {requests}\n\n<b>Статус</b> - {status}\n<b>Закончится</b> - {data}', parse_mode="HTML")


# @router.callback_query(lambda c: c.data.startswith('search_chatgpt'))
# async def buy_vip(message: Message):
#     if 'Default' in DB.get_status(message.from_user.id):
#         secret_key = secrets.token_urlsafe()
#         pay_link = payment.create_paylink(secret_key)
#         # DB.write_payment_token(message.from_user.id, secret_key)
#         await bot.send_message(message.from_user.id, '<b>Название:</b> VIP\n<b>Стоимость:</b> 149₽\n<b>Срок действия:</b> 30 дней', reply_markup=keyboards.create_pay_button(pay_link), parse_mode="HTML")
#     else:
#         await bot.send_message(message.from_user.id, 'Подписка уже активна!')
#
#
# @router.callback_query(lambda c: c.data.startswith('search_chatgpt'))
# async def check_payment(message: Message):
#     # secret_key = DB.get_temp_payment_token(message.from_user.id)
#     payment_status = payment.check_pay_status(secret_key)
#     if payment_status is not None and 'success' in payment_status:
#         await bot.send_message(message.from_user.id, '✅ Успешная оплата!')
#         DB.success_pay(message.from_user.id, date.today())
#         DB.write_payment_token(message.from_user.id, 0)
#     else:
#         await bot.send_message(message.from_user.id, '❌ Вы еще не оплатили!')


@router.message(F.photo)
async def accepting_image(message: Message, state: FSMContext):
    await add_user(message.from_user.id)

    num = random.randint(1, 9568957)
    content = os.listdir('images')
    if f'{num}.png' in content:
        while True:
            # print('Create new "num" for name IMG')
            num = random.randint(1, 9568957)
            content = os.listdir('images')
            if f'{num}.png' in content:
                pass
            else:
                break

    await bot.download(message.photo[-1], destination=f'images/{num}.png')

    result = await aiopytesseract.image_to_string(Path(f'images/{num}.png').read_bytes(), tessdata_dir='tesseract-main/tessdata',lang='eng+rus')

    os.remove(f'images/{num}.png')

    if result != "":
        msg = await message.answer(f'{result}', reply_markup=buttons_under_answer.as_markup())
        await add_requests('images_sent', message.from_user.id)  # TYPES: text_translate; chatgpt_search; images_sent
        await state.update_data({"msg_id": msg.message_id})
        await state.update_data({"result": result})
        await state.update_data({"user_id": message.from_user.id})

        state_data = await state.get_data()

        last_result_for_gpt = state_data.get('last_result_for_gpt')
        last_result_for_translate = state_data.get('last_result_for_translate')
        if last_result_for_gpt is None:
            await state.update_data({"last_result_for_gpt": result})
        if last_result_for_translate is None:
            await state.update_data({"last_result_for_translate": result})

    else:
        await message.answer(f'На Изображении/Скрине/Фотографии должен быть текст!', parse_mode="HTML")


@router.callback_query(lambda c: c.data.startswith('back_to_text'))
async def back_to_text(callback_query, state: FSMContext):
    try:
        result, user_id, msg_id = (await state.get_data())['result'], (await state.get_data())['user_id'], (await state.get_data())['msg_id']
        await add_user(user_id)
        await bot.edit_message_text(message_id=msg_id, chat_id=user_id, text=f'{result}', reply_markup=buttons_under_answer.as_markup())
    except:
        await callback_query.message.answer(f'Ошибка! Повторите попытку.')

    await callback_query.answer()


@router.callback_query(lambda c: c.data.startswith('search_chatgpt'))
async def search_chatgpt(callback_query, state: FSMContext):
    user_id = (await state.get_data())['user_id']
    status = await get_status(user_id)

    if status == 'Beta-test' or 'Admin':
        try:
            state_data = await state.get_data()
            ready_chatgpt_answer = state_data.get('chatgpt_answer')
            result, msg_id, last_result_for_gpt = (await state.get_data())['result'], (await state.get_data())['msg_id'], (await state.get_data())['last_result_for_gpt']
            await add_user(user_id)

            if ready_chatgpt_answer is None or result != last_result_for_gpt:
                giga = GigaChatAsyncClient(credentials='OGNiYTIyMDktMWVlYy00NWYzLWJlODctZWRiMzc5N2MxZTlmOjI2OGI4MWI3LWU1OTYtNGViYS1hMzRjLWNjMjBhOWNjMTgzOQ==', scope="GIGACHAT_API_PERS", verify_ssl_certs=False)
                response = await giga.achat(F"{result}")
                await bot.edit_message_text(message_id=msg_id, chat_id=user_id, text=f'{response.choices[0].message.content}', reply_markup=back.as_markup())
                await state.update_data({"chatgpt_answer": response.choices[0].message.content})
                await state.update_data({"last_result_for_gpt": result})
                await add_requests('chatgpt_search', user_id)  # TYPES: text_translate; chatgpt_search; images_sent
            else:
                await bot.edit_message_text(message_id=msg_id, chat_id=user_id, text=f'{ready_chatgpt_answer}', reply_markup=back.as_markup())

        except:
            await callback_query.message.answer(f'Ошибка! Повторите попытку.')
    else:
        await callback_query.message.answer(f'Для данного Запроса ваш статус Должен быть выше!')

    await callback_query.answer()


@router.callback_query(lambda c: c.data.startswith('translate_text'))
async def translate_text(callback_query, state: FSMContext):
    try:
        state_data = await state.get_data()
        ready_translated_text = state_data.get('translated_text')
        result, user_id, msg_id, last_result_for_translate = (await state.get_data())['result'], (await state.get_data())['user_id'], (await state.get_data())['msg_id'], (await state.get_data())['last_result_for_translate']
        await add_user(user_id)

        if ready_translated_text is None or result != last_result_for_translate:
            translator = Translator()
            translations = await translator.translate(text=result, dest="ru")
            await bot.edit_message_text(message_id=msg_id, chat_id=user_id, text=f'{translations.text}', reply_markup=back.as_markup())
            await state.update_data({"translated_text": translations.text})
            await state.update_data({"last_result_for_translate": result})
            await add_requests('text_translate', user_id)  # TYPES: text_translate; chatgpt_search; images_sent
        else:
            await bot.edit_message_text(message_id=msg_id, chat_id=user_id, text=f'{ready_translated_text}', reply_markup=back.as_markup())

    except:
        await callback_query.message.answer(f'Ошибка! Повторите попытку.')

    await callback_query.answer()