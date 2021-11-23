from app.app import App
from app.jinja import custom_jinja
from app.routers import init_routers
from app.telegram import Telegram
from mb_base1.jinja import Templates
from mb_base1.server import Server

app = App()
templates = Templates(app, custom_jinja)
server = Server(app, Telegram(app), init_routers(app, templates), templates).get_server()
