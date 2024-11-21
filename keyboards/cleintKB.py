from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram import types

buttons_under_answer = InlineKeyboardBuilder()
back = InlineKeyboardBuilder()

main_keyboard = [
    [KeyboardButton(text='Помощь')],
    [KeyboardButton(text='Профиль')],
]

back.row(types.InlineKeyboardButton(
    text='Назад', callback_data='back_to_text')
)

buttons_under_answer.row(types.InlineKeyboardButton(
    text='Перевести на Русский', callback_data='translate_text')
)

buttons_under_answer.row(types.InlineKeyboardButton(
    text='Поиск ответа ChatGPT', callback_data='search_chatgpt')
)

kb_client = ReplyKeyboardMarkup(resize_keyboard=True, keyboard=main_keyboard)

