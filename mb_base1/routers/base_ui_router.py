from fastapi import APIRouter
from mb_std import md
from mb_std.mongo import make_query
from starlette.requests import Request
from starlette.responses import HTMLResponse
from wtforms import BooleanField, Form, IntegerField, SelectField, TextAreaField

from mb_base1.app import BaseApp
from mb_base1.jinja import Templates, flash, form_choices
from mb_base1.models import DConfigType
from mb_base1.telegram import BaseTelegram
from mb_base1.utils import depends_form, redirect


class ImportDConfigForm(Form):
    yaml_data = TextAreaField(render_kw={"rows": 20})


class DLogsFilterForm(Form):
    category = SelectField()
    limit = IntegerField(default=100)


class UpdateValueForm(Form):  # for dconfig and dvalue
    yaml_value = TextAreaField(render_kw={"rows": 20})
    multiline_string = BooleanField()


class UpdateDConfigMultilineForm(Form):
    value = TextAreaField(render_kw={"rows": 20})


def init(app: BaseApp, templates: Templates, telegram: BaseTelegram) -> APIRouter:
    router = APIRouter()

    @router.get("/system", response_class=HTMLResponse)
    def system_page(req: Request):
        stats = app.system_service.get_stats()
        telegram_is_started = telegram.is_started
        return templates.render(req, "system.j2", md(stats, telegram_is_started))

    @router.get("/dconfig", response_class=HTMLResponse)
    def dconfig_page(req: Request):
        return templates.render(req, "dconfig.j2")

    @router.get("/update-dconfig", response_class=HTMLResponse)
    def update_dconfig_page(req: Request):
        form = ImportDConfigForm()
        return templates.render(req, "update_dconfig.j2", md(form))

    @router.get("/update-dconfig-multiline/{key}", response_class=HTMLResponse)
    def update_dconfig_multiline_page(req: Request, key):
        form = UpdateDConfigMultilineForm(data={"value": app.dconfig.get(key)})
        return templates.render(req, "update_dconfig_multiline.j2", md(form, key))

    @router.get("/dvalue", response_class=HTMLResponse)
    def dvalue_page(req: Request):
        return templates.render(req, "dvalue.j2")

    @router.get("/update-dvalue/{key}", response_class=HTMLResponse)
    def update_dvalue_page(req: Request, key: str):
        form = UpdateValueForm(yaml_value=app.dvalue_service.get_dvalue_yaml_value(key))
        return templates.render(req, "update_dvalue.j2", md(form, key))

    @router.get("/dlogs", response_class=HTMLResponse)
    def dlogs_page(req: Request):
        category_stats = {}
        for category in app.dlog_collection.collection.distinct("category"):
            category_stats[category] = app.dlog_collection.count(md(category))
        form = DLogsFilterForm(req.query_params)
        form.category.choices = form_choices(list(category_stats.keys()), title="category")
        query = make_query(category=form.data["category"])
        dlogs = app.dlog_collection.find(query, "-created_at", form.data["limit"])
        return templates.render(req, "dlogs.j2", md(dlogs, form, category_stats))

    # actions

    @router.post("/update-dconfig-admin")
    def update_dconfig_admin(req: Request, form_data=depends_form):
        data = {
            x: form_data.get(x) for x in app.dconfig.get_non_hidden_keys() if app.dconfig.get_type(x) != DConfigType.MULTILINE
        }
        app.dconfig_service.update(data)
        flash(req, "dconfigs were updated")
        return redirect("/dconfig")

    @router.post("/update-dconfig-yaml")
    def update_dconfig_yaml(form_data=depends_form):
        return app.dconfig_service.update_dconfig_yaml(form_data["yaml_data"])

    @router.post("/update-dvalue/{key}")
    def update_dvalue(key: str, form_data=depends_form):
        form = UpdateValueForm(form_data)
        app.dvalue_service.set_dvalue_yaml_value(key, form.yaml_value.data, form.multiline_string.data)
        return redirect("/dvalue")

    @router.post("/update-dconfig-multiline/{key}")
    def update_dconfig_multiline(req: Request, key, form_data=depends_form):
        form = UpdateDConfigMultilineForm(form_data)
        if form.validate():
            app.dconfig_service.update_multiline(key, form.data["value"])
            flash(req, f"dconfig '{key}' was updated")
            return redirect(f"/update-dconfig-multiline/{key}")
        return {"errors": form.errors}

    return router
