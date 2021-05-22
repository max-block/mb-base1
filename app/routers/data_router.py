from typing import Optional

from fastapi import APIRouter
from mb_commons.mongo import make_query

from app.app import App
from app.models import DataStatus
from mb_base1.utils import j


def init(app: App) -> APIRouter:
    router = APIRouter()

    @router.get("")
    def get_data_list(worker: Optional[str] = None, status: Optional[DataStatus] = None, limit: int = 100):
        return app.db.data.find(make_query(worker=worker, status=status), "-created_at", limit)

    @router.post("/generate")
    def generate_data():
        return j(app.data_service.generate_data())

    @router.get("/{pk}")
    def get_data(pk):
        return app.db.data.get_or_none(pk)

    @router.delete("/{pk}")
    def delete_data(pk):
        return j(app.db.data.delete_by_id(pk))

    return router
