from fastapi import APIRouter
from mb_std import md
from mb_std.mongo import make_query
from starlette.requests import Request
from starlette.responses import HTMLResponse
from wtforms import Form, IntegerField, SelectField

from app.app import App
from app.models import DataStatus
from mb_base1.jinja import Templates, form_choices


class DataFilterForm(Form):
    status = SelectField(choices=form_choices(DataStatus, title="status"), default="")
    limit = IntegerField(default=100)


def init(app: App, templates: Templates) -> APIRouter:
    router = APIRouter()

    @router.get("/", response_class=HTMLResponse)
    def index_page(req: Request):
        return templates.render(req, "index.j2")

    @router.get("/data", response_class=HTMLResponse)
    def data_page(req: Request):
        form = DataFilterForm(req.query_params)
        query = make_query(status=form.data["status"])
        data = app.db.data.find(query, "-created_at", form.data["limit"])
        return templates.render(req, "data.j2", md(form, data))

    return router
