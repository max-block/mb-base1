import functools
from threading import Thread
from typing import Optional

from telebot import TeleBot
from telebot.types import Message
from telebot.util import split_string
from wrapt import synchronized

from app.app import App


class BaseTelegram:
    """Telegram is an alternative UI to the web API for the project. It works via telegram commands.
    If you need just to send a message to the project channel / group, use core.send_telegram_message()"""

    def __init__(self, app: App):
        self.app = app
        self.bot: Optional[TeleBot] = None
        self.is_started = False
        self.admins: list[int] = []

    @synchronized
    def start(self) -> Optional[str]:
        """
        Telegram bot can be started only if these bot settings are set:
        - telegram_token
        - telegram_admins
        - telegram_polling
        """
        telegram_token = self.app.dconfig.get("telegram_token")
        telegram_polling = self.app.dconfig.get("telegram_polling")

        try:
            self.admins = []
            for admin in self.app.dconfig.get("telegram_admins", "").split(","):
                admin = admin.strip()
                if admin:
                    self.admins.append(int(admin))
        except Exception as e:
            self.app.dlog("telegram_parse_admins", {"error": str(e)})
            return f"telegram_parse_admins: {str(e)}"

        if telegram_token and telegram_polling and self.admins:
            Thread(target=self._start, args=(telegram_token,)).start()
            return None
        else:
            return "there are some unset configs: telegram_token or telegram_polling or telegram_admins"

    def _start(self, token: str):
        try:
            self.bot = TeleBot(token, skip_pending=True)
            self._init_base_commands()
            self.init_commands()
            self.is_started = True
            self.app.logger.debug("telegram started")
            self.bot.polling(none_stop=True)

        except Exception as e:
            self.is_started = False
            self.app.dlog("telegram_polling", {"error": str(e)})
            self.app.logger.error(f"telegram polling: {str(e)}")

    @synchronized
    def stop(self):
        self.is_started = False
        if self.bot:
            self.bot.stop_bot()
        self.app.logger.debug("telegram stopped")

    def _init_base_commands(self):
        @self.bot.message_handler(commands=["start", "help"])
        @self.auth(admins=self.admins, bot=self.bot)
        def help_handler(message: Message):
            self._send_message(message.chat.id, self.app.app_config.telegram_bot_help)

        @self.bot.message_handler(commands=["ping"])
        @self.auth(admins=self.admins, bot=self.bot)
        def ping_handler(message: Message):
            text = message.text.replace("/ping", "").strip()
            self._send_message(message.chat.id, f"pong {text}")

    def init_commands(self):
        pass

    def _send_message(self, chat_id: int, message: str):
        for text in split_string(message, 4096):
            self.bot.send_message(chat_id, text)  # type:ignore

    def send_to_channel(self, message: str):
        self._send_message(self.app.dconfig.get("telegram_chat_id"), message)  # type:ignore

    @staticmethod
    def auth(*, admins: list[int], bot: TeleBot):
        def outer(func):
            @functools.wraps(func)
            def wrapper(message: Message):
                if message.chat.id in admins:
                    return func(message)
                else:
                    bot.send_message(message.chat.id, "Who are you?")

            return wrapper

        return outer
