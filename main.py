from aiogram import executor
import handler
from create_bot import dp


async def start(_):
    print('Бот запущен')


handler.register(dp)


if __name__ == "__main__":
    # Запуск бота
    handler.scheduler.start()
    executor.start_polling(dp, skip_updates=True, on_startup=start)
