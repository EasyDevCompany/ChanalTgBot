import datetime
import os
from create_bot import bot
from aiogram import Dispatcher, types
from aiogram.dispatcher.filters import Command
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from parsing import (get_urgent_information, get_horoscope, get_weather_today,
                     get_holidays, get_urgent_information_polling,
                     get_weather_tomorrow, get_info_from_bga,
                     get_info_from_bryanskobl, get_info_from_newbryansk,
                     get_info_from_ria)
from dotenv import load_dotenv
import logging

load_dotenv()

scheduler = AsyncIOScheduler(timezone='UTC')


async def send_urgent_info(id):
    ads = get_urgent_information()
    message = 'Сводка новостей за прошедшие сутки\n\n'
    for ad in ads.items():
        message += f'{ad[0]}\n{ad[1]}\n\n'
    await bot.send_message(id, message, parse_mode='HTML')


async def send_horoscope(id):
    today = datetime.datetime.now().strftime('%d.%m.%Y года')
    await bot.send_message(id, f'ГОРОСКОП НА {today}')
    horoscopes = get_horoscope()
    for horoscope in horoscopes.items():
        await bot.send_message(id,
                               f'{horoscope[0]}\n\n{horoscope[1]}',
                               parse_mode='HTML')


async def send_forecast_today(id):
    today = datetime.datetime.now().strftime('%d.%m.%Y года')
    forecasts = get_weather_today()
    message = f'ПРОГНОЗ ПОГОДЫ на {today}\n\n'
    for forecast in forecasts:
        message += forecast + '\n'
    await bot.send_message(id, message)


async def send_forecast_tomorrow(id):
    tomorrow = (datetime.datetime.now() + datetime.timedelta(1)
                ).strftime('%d.%m.%Y года')
    forecasts = get_weather_tomorrow()
    message = f'ПРОГНОЗ ПОГОДЫ на {tomorrow}\n\n'
    for forecast in forecasts:
        message += forecast + '\n'
    await bot.send_message(id, message)


async def send_holidays(id):
    today = datetime.datetime.now().strftime('%d.%m.%Y года')
    holidays = get_holidays()
    message = f'ПРАЗДНИКИ {today}\n\n'
    for holiday in holidays:
        message += '🎉' + holiday + '\n'
    await bot.send_message(id, message)


async def send_info_polling(id):
    thing = get_urgent_information_polling()
    if thing is not None:
        try:
            await bot.send_photo(id, thing[0], caption=thing[1], parse_mode='HTML')
        except Exception as e:
            await bot.send_message(id, thing[1], parse_mode='HTML')
            logging.error('Невозможно прикрепить картинку')
            logging.error(e)


async def send_info_newbryansk_polling(id):
    thing = get_info_from_newbryansk()
    if thing is not None:
        await bot.send_photo(id, thing[0], caption=thing[1], parse_mode='HTML')


async def send_info_ria_polling(id):
    thing = get_info_from_ria()
    if thing is not None:
        await bot.send_photo(id, thing[0], caption=thing[1], parse_mode='HTML')


async def send_info_bga_polling(id):
    thing = get_info_from_bga()
    if thing is not None:
        await bot.send_photo(id, thing[0], caption=thing[1], parse_mode='HTML')


async def send_info_bo_polling(id):
    thing = get_info_from_bryanskobl()
    try:
        if thing is not None:
            await bot.send_photo(id, thing[0],
                                 caption=thing[1], parse_mode='HTML')
    except Exception:
        await bot.send_message(id, thing[1], parse_mode='HTML')


async def start(message: types.Message):
    cnl_id = os.getenv('CHANNEL_ID')
    scheduler.add_job(send_urgent_info, 'cron',
                      args=[cnl_id], hour=4, misfire_grace_time=None)
    scheduler.add_job(send_horoscope, 'cron', args=[cnl_id],
                      hour=4, minute=45, misfire_grace_time=None)
    scheduler.add_job(send_forecast_today, 'cron', args=[cnl_id],
                      hour=4, minute=30, misfire_grace_time=None)
    scheduler.add_job(send_holidays, 'cron', args=[cnl_id],
                      hour=6, misfire_grace_time=None)
    scheduler.add_job(send_info_polling, 'interval',
                      args=[cnl_id], minutes=1, misfire_grace_time=None)
    scheduler.add_job(send_info_newbryansk_polling, 'interval',
                      args=[cnl_id], minutes=1, seconds=3,
                      misfire_grace_time=None)
    scheduler.add_job(send_info_ria_polling, 'interval',
                      args=[cnl_id], minutes=1,
                      seconds=6, misfire_grace_time=None)
    scheduler.add_job(send_info_bga_polling, 'interval',
                      args=[cnl_id], minutes=1,
                      seconds=9, misfire_grace_time=None)
    scheduler.add_job(send_info_bo_polling, 'interval',
                      args=[cnl_id], minutes=1, seconds=12,
                      misfire_grace_time=None)
    scheduler.add_job(send_forecast_tomorrow, 'cron', args=[cnl_id],
                      hour=18, misfire_grace_time=None)


def register(dp: Dispatcher):
    dp.register_message_handler(start, Command('start'))
