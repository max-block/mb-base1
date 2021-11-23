import json
import time
from dataclasses import asdict, is_dataclass
from datetime import date, datetime
from decimal import Decimal
from enum import Enum
from json import JSONEncoder

from bson import ObjectId
from fastapi import Depends
from mb_commons import Result
from mb_commons.mongo import MongoModel
from pymongo.results import DeleteResult, InsertManyResult, InsertOneResult, UpdateResult
from starlette.requests import Request
from starlette.responses import PlainTextResponse, RedirectResponse, Response
from starlette.status import HTTP_303_SEE_OTHER
from telebot import TeleBot
from telebot.util import split_string
from wrapt import synchronized


class CustomJSONEncoder(JSONEncoder):
    def default(self, o):

        if isinstance(o, Decimal):
            return str(o)
        if isinstance(o, (datetime, date)):
            return o.isoformat()
        if is_dataclass(o):
            return asdict(o)
        if isinstance(o, Enum):
            return o.value
        if isinstance(o, MongoModel):
            return o.dict()
        if isinstance(o, (DeleteResult, UpdateResult)):
            return o.raw_result
        if isinstance(o, InsertOneResult):
            return o.inserted_id
        if isinstance(o, InsertManyResult):
            return o.inserted_ids
        if isinstance(o, ObjectId):
            return str(o)

        return JSONEncoder.default(self, o)


async def get_form_data(request: Request):
    return await request.form()


depends_form = Depends(get_form_data)


def plain_text(content) -> PlainTextResponse:
    return PlainTextResponse(content)


def redirect(url: str) -> RedirectResponse:
    return RedirectResponse(url, status_code=HTTP_303_SEE_OTHER)


def j(data) -> Response:
    json_str = json.dumps(data, cls=CustomJSONEncoder).encode("utf-8")
    return Response(media_type="application/json", content=json_str)


def get_registered_attributes(dconfig):
    return [x for x in dir(dconfig) if not x.startswith("_")]


@synchronized
def send_telegram_message(token: str, chat_id: int, message: str) -> Result[bool]:
    bot = TeleBot(token)
    try:
        for text in split_string(message, 4096):
            bot.send_message(chat_id, text)
            time.sleep(1)
        return Result(ok=True)
    except Exception as e:
        return Result(error=str(e))
    finally:
        bot.stop_bot()
        bot.close()
