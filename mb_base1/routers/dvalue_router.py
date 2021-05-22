from fastapi import APIRouter

from mb_base1.app import BaseApp
from mb_base1.utils import plain_text


def init(app: BaseApp) -> APIRouter:
    router = APIRouter()

    @router.get("")
    def get_dvalues():
        return app.dvalue_collection.find({})

    @router.get("/yaml")
    def get_dvalues_yaml():
        return plain_text(app.dvalue_service.get_dvalues_yaml())

    @router.get("/{pk}")
    def get_dvalue(pk):
        return app.dvalue_collection.get_or_none(pk)

    @router.get("/{pk}/value")
    def get_dvalue_value(pk):
        return app.dvalue.get(pk)

    @router.get("/{pk}/yaml")
    def get_dvalue_yaml(pk):
        return plain_text(app.dvalue_service.get_dvalue_yaml_value(pk))

    return router
