import asyncio

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from aiogram.methods import DeleteWebhook

from config_reader import config
from handlers import client, admin

bot = Bot(config.bot_token.get_secret_value())


async def on_startup(dispatcher):
    print("Бот успешно запущен!")


async def main():
    dp = Dispatcher(storage=MemoryStorage())

    dp.include_routers(client.router, admin.router)

    dp.startup.register(on_startup)
    await bot(DeleteWebhook(drop_pending_updates=True))
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())