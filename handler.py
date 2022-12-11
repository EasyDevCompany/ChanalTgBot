from create_bot import bot
from aiogram import Dispatcher, types
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from parsing import get_urgent_information, get_horoscope, get_weather


scheduler = AsyncIOScheduler(timezone='UTC')


async def send_urgent_info(id):
    ads = get_urgent_information()
    for ad in ads.items():
        await bot.send_message(id,
                               f'{ad[0]}\n{ad[1]}', parse_mode='HTML')


async def send_horoscope(id):
    horoscopes = get_horoscope()
    for horoscope in horoscopes.items():
        await bot.send_message(id,
                               f'{horoscope[0]}\n\n{horoscope[1]}',
                               parse_mode='HTML')


async def send_forecast(id):
    forecasts = get_weather()
    for forecast in forecasts:
        await bot.send_message(id, forecast)


async def start(message: types.Message):
    bot_obj = await bot.get_me()
    bot_id = bot_obj.id
    for chat_member in message.new_chat_members:
        if chat_member.id == bot_id:
            await message.reply("Привет!\nЯ Брянский бот!")
    scheduler.add_job(send_urgent_info, 'cron', args=[message.chat.id], hour=4)
    scheduler.add_job(send_horoscope, 'cron',
                      args=[message.chat.id], hour=4, minute=45)
    scheduler.add_job(send_forecast, 'cron', args=[message.chat.id],
                      hour=4, minute=30)


def register(dp: Dispatcher):
    dp.register_message_handler(start, content_types=['new_chat_members'])
