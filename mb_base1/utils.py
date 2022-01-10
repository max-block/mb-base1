import time

from fastapi import Depends
from mb_std import Result
from starlette.requests import Request
from starlette.responses import PlainTextResponse, RedirectResponse
from starlette.status import HTTP_303_SEE_OTHER
from telebot import TeleBot
from telebot.util import split_string
from wrapt import synchronized


async def get_form_data(request: Request):
    return await request.form()


depends_form = Depends(get_form_data)


def plain_text(content) -> PlainTextResponse:
    return PlainTextResponse(content)


def redirect(url: str) -> RedirectResponse:
    return RedirectResponse(url, status_code=HTTP_303_SEE_OTHER)


def get_registered_attributes(dconfig):
    return [x for x in dir(dconfig) if not x.startswith("_")]


@synchronized
def send_telegram_message(token: str, chat_id: int, message: str) -> Result[bool]:
    bot = TeleBot(token)
    try:
        for text in split_string(message, 4096):
            bot.send_message(chat_id, text)
            time.sleep(3)
        return Result(ok=True)
    except Exception as e:
        return Result(error=str(e))
