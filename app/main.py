from app.app import App
from app.jinja import custom_jinja
from app.routers import data_router, ui_router
from app.telegram import Telegram
from mb_base1.jinja import Templates
from mb_base1.server import AppRouter, Server

app = App()
templates = Templates(app, custom_jinja)
routers = [AppRouter(data_router.init(app), prefix="/api/data", tag="data"), AppRouter(ui_router.init(app, templates), tag="ui")]
server = Server(app, Telegram(app), routers, templates).get_server()
