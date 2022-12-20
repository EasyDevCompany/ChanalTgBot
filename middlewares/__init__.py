from aiogram import Dispatcher

from .throttling import ThrottlingMiddleware, UrlMiddleWare


def setup(dp: Dispatcher):
    dp.middleware.setup(ThrottlingMiddleware())
    dp.middleware.setup(UrlMiddleWare())
