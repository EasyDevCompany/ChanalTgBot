from create_bot import bot
from aiogram import Dispatcher, types
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from parsing import (get_urgent_information, get_horoscope, get_weather_today,
                     get_holidays, get_urgent_information_polling,
                     get_weather_tomorrow, get_info_from_bga,
                     get_info_from_bryanskobl, get_info_from_newbryansk,
                     get_info_from_ria)


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


async def send_forecast_today(id):
    forecasts = get_weather_today()
    for forecast in forecasts:
        await bot.send_message(id, forecast)


async def send_forecast_tomorrow(id):
    forecasts = get_weather_tomorrow()
    for forecast in forecasts:
        await bot.send_message(id, forecast)


async def send_holidays(id):
    holidays = get_holidays()
    for holiday in holidays:
        await bot.send_message(id, holiday)


async def send_info_polling(id):
    thing = get_urgent_information_polling()
    if thing is not None:
        await bot.send_message(
            id,
            f'{list(thing.keys())[0]}\n\n{list(thing.values())[0]}',
            parse_mode='HTML')


async def send_info_newbryansk_polling(id):
    thing = get_info_from_newbryansk()
    if thing is not None:
        await bot.send_message(
            id,
            f'{list(thing.keys())[0]}\n\n{list(thing.values())[0]}',
            parse_mode='HTML')


async def send_info_ria_polling(id):
    thing = get_info_from_ria()
    if thing is not None:
        await bot.send_message(
            id,
            f'{list(thing.keys())[0]}\n\n{list(thing.values())[0]}',
            parse_mode='HTML')


async def send_info_bga_polling(id):
    thing = get_info_from_bga()
    if thing is not None:
        await bot.send_message(
            id,
            f'{list(thing.keys())[0]}\n\n{list(thing.values())[0]}',
            parse_mode='HTML')


async def send_info_bo_polling(id):
    thing = get_info_from_bryanskobl()
    if thing is not None:
        await bot.send_message(
            id,
            f'{list(thing.keys())[0]}\n\n{list(thing.values())[0]}',
            parse_mode='HTML')


async def start(message: types.Message):
    bot_obj = await bot.get_me()
    bot_id = bot_obj.id
    for chat_member in message.new_chat_members:
        if chat_member.id == bot_id:
            await message.reply("Привет!\nЯ Брянский бот!")
    scheduler.add_job(send_urgent_info, 'cron', args=[message.chat.id], hour=4)
    scheduler.add_job(send_horoscope, 'cron',
                      args=[message.chat.id], hour=4, minute=45)
    scheduler.add_job(send_forecast_today, 'cron', args=[message.chat.id],
                      hour=4, minute=30)
    scheduler.add_job(send_holidays, 'cron', args=[message.chat.id], hour=6)
    scheduler.add_job(send_info_polling, 'interval',
                      args=[message.chat.id], minutes=1)
    scheduler.add_job(send_info_newbryansk_polling, 'interval',
                      args=[message.chat.id], minutes=1, seconds=3)
    scheduler.add_job(send_info_ria_polling, 'interval',
                      args=[message.chat.id], minutes=1, seconds=6)
    scheduler.add_job(send_info_bga_polling, 'interval',
                      args=[message.chat.id], minutes=1, seconds=9)
    scheduler.add_job(send_info_bo_polling, 'interval',
                      args=[message.chat.id], minutes=1, seconds=12)
    scheduler.add_job(send_forecast_tomorrow, 'cron', args=[message.chat.id],
                      hour=18)


def register(dp: Dispatcher):
    dp.register_message_handler(start, content_types=['new_chat_members'])
