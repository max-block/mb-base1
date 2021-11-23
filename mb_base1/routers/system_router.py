import tracemalloc

from fastapi import APIRouter
from starlette.responses import PlainTextResponse

from mb_base1.app import BaseApp
from mb_base1.telegram import BaseTelegram


def init(app: BaseApp, telegram: BaseTelegram) -> APIRouter:
    router = APIRouter()

    @router.get("/logfile", response_class=PlainTextResponse)
    def view_logfile():
        return app.system_service.read_logfile()

    @router.delete("/logfile")
    def clean_logfile():
        app.system_service.clean_logfile()
        return True

    @router.post("/tracemalloc/start")
    def start_tracemalloc():
        tracemalloc.start()
        return {"message": "tracemalloc was started"}

    @router.post("/tracemalloc/stop")
    def stop_tracemalloc():
        tracemalloc.stop()
        return {"message": "tracemalloc was stopped"}

    @router.get("/tracemalloc/snapshot", response_class=PlainTextResponse)
    def snapshot_tracemalloc():
        return app.system_service.tracemalloc_snapshot()

    @router.post("/test-telegram-message")
    def test_telegram_message():
        message = "bla bla bla " * 10
        return app.send_telegram_message(message)

    @router.get("/telegram-bot")
    def get_telegram_bot_status():
        return telegram.is_started

    @router.post("/telegram-bot/start")
    def start_telegram_bot():
        err = telegram.start()
        return {"error": err} if err else True

    @router.post("/telegram-bot/stop")
    def stop_telegram_bot():
        return telegram.stop()

    return router
