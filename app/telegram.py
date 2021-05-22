from telebot.types import Message

from app.app import App
from mb_base1.telegram import BaseTelegram


class Telegram(BaseTelegram):
    def __init__(self, app: App):
        super().__init__(app)

    def init_commands(self):
        @self.bot.message_handler(commands=["ping2"])
        @self.auth(admins=self.admins, bot=self.bot)
        def ping_handler(message: Message):
            text = message.text.replace("/ping", "").strip()
            self._send_message(message.chat.id, f"pong pong {text}")
