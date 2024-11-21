from aiogram import types, Router
from aiogram.filters import Command
from database import *

router = Router()

admin_id = 123123123

@router.message(Command(commands=["lll"]))
async def admin_command(message: types.Message):

    if message.from_user.id == admin_id:
        types_of_requests, requests = ['text_translate', 'chatgpt_search', 'images_sent'], []

        last_id = await get_last_id()
        iteration_types, iterations_id = 0, 0
        stats = ''
        for user_id in range(1, last_id + 1):
            for type_of_request in types_of_requests:
                number_of_request = await get_requests(user_id, None, type_of_request)
                if iterations_id != 0:
                    req = requests[iteration_types]
                    number_of_request = number_of_request + req
                    requests[iteration_types] = number_of_request
                    if iteration_types == 2:
                        iteration_types = 0
                    else:
                        iteration_types += 1
                else:
                    requests.append(number_of_request)
            iterations_id += 1
        for i in range(3):
            stats = stats + f'{types_of_requests[i]}: {requests[i]}\n'
        await message.answer(text=f'Статистика бота\n\nall users: {last_id}\n{stats}')
