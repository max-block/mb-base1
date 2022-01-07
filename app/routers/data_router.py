from fastapi import APIRouter
from mb_std import md
from mb_std.mongo import make_query
from starlette.requests import Request

from app.app import App
from app.models import DataStatus


def init(app: App) -> APIRouter:
    router = APIRouter()

    @router.get("/post/{url:path}")
    def test(url: str, request: Request):
        return md(url, request.query_params)

    @router.get("")
    def get_data_list(worker: str | None = None, status: DataStatus | None = None, limit: int = 100):
        return app.db.data.find(make_query(worker=worker, status=status), "-created_at", limit)

    @router.post("/generate")
    def generate_data():
        return app.data_service.generate_data()

    @router.get("/{pk}")
    def get_data(pk):
        return app.db.data.get_or_none(pk)

    @router.post("/{pk}/inc")
    def inc_data(pk, value: int | None = None):
        return app.db.data.find_by_id_and_update(pk, {"$inc": {"value": value or 1}})

    @router.delete("/{pk}")
    def delete_data(pk):
        return app.db.data.delete_by_id(pk)

    return router
