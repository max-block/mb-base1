from app.app import App
from app.routers import data_router, ui_router
from mb_base1.server import AppRouter


def init_routers(app: App, templates):
    return [
        AppRouter(data_router.init(app), prefix="/api/data", tag="data"),
        AppRouter(ui_router.init(app, templates), tag="ui"),
    ]
