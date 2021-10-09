import json
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from functools import partial
from typing import Callable, Optional, Type, Union

from jinja2 import ChoiceLoader, Environment, PackageLoader
from markupsafe import Markup
from starlette.responses import HTMLResponse

from mb_base1.app import BaseApp
from mb_base1.utils import CustomJSONEncoder


def dlog_data_truncate(data) -> str:
    if not data:
        return ""
    res = json.dumps(data, cls=CustomJSONEncoder)
    if len(res) > 100:
        return res[:100] + "..."
    return res


def timestamp(value: Optional[Union[datetime, int]], format_: str = "%Y-%m-%d %H:%M:%S") -> str:
    if isinstance(value, datetime):
        return value.strftime(format_)
    if isinstance(value, int):
        return datetime.fromtimestamp(value).strftime(format_)
    return ""


def empty(value):
    return value if value else ""


def yes_no(value, is_colored=True, hide_no=False, none_is_false=False, on_off=False):
    clr = "black"
    if none_is_false and value is None:
        value = False

    if value is True:
        value = "on" if on_off else "yes"
        clr = "green"
    elif value is False:
        if hide_no:
            value = ""
        else:
            value = "off" if on_off else "no"
        clr = "red"
    elif value is None:
        value = ""
    if not is_colored:
        clr = "black"
    return Markup(f"<span style='color: {clr};'>{value}</span>")


def json_url_encode(data: dict) -> str:
    return json.dumps(data)


def nformat(value, prefix="", suffix="", separator="", hide_zero=True, digits=2):
    if value is None or value == "":
        return ""
    if float(value) == 0:
        if hide_zero:
            return ""
        else:
            return f"{prefix}0{suffix}"
    if float(value) > 1000:
        value = "".join(
            reversed([x + (separator if i and not i % 3 else "") for i, x in enumerate(reversed(str(int(value))))]),
        )
    else:
        value = round(value, digits)

    return f"{prefix}{value}{suffix}"


def raise_(msg):
    raise Exception(msg)


def form_choices(choices: Union[list[str], Type[Enum]], title=""):
    result = []
    if title:
        result.append(("", title + "..."))
    if isinstance(choices, list):
        for value in choices:
            result.append((value, value))
    else:
        for value in [e.value for e in choices]:
            result.append((value, value))
    return result


@dataclass
class CustomJinja:
    header_info: Optional[Callable] = None
    header_info_new_line: bool = False
    footer_info: Optional[Callable] = None
    filters: Optional[dict] = None
    globals: Optional[dict] = None


def _default_info(_app):
    return ""


class Templates:
    def __init__(self, app: BaseApp, custom_jinja: CustomJinja):
        env = Environment(loader=ChoiceLoader([PackageLoader("mb_base1"), PackageLoader("app")]))  # nosec
        env.filters["timestamp"] = timestamp
        env.filters["dt"] = timestamp
        env.filters["empty"] = empty
        env.filters["yes_no"] = yes_no
        env.filters["nformat"] = nformat
        env.filters["n"] = nformat
        env.filters["json_url_encode"] = json_url_encode
        env.filters["dlog_data_truncate"] = dlog_data_truncate
        env.globals["app_config"] = app.app_config
        env.globals["dconfig"] = app.dconfig
        env.globals["dvalue"] = app.dvalue
        env.globals["now"] = datetime.utcnow
        env.globals["raise"] = raise_

        env.globals["confirm"] = Markup(""" onclick="return confirm('sure?')" """)
        if custom_jinja.filters:
            env.filters.update(custom_jinja.filters)
        if custom_jinja.globals:
            env.globals.update(custom_jinja.globals)

        header_info = custom_jinja.header_info or _default_info
        footer_info = custom_jinja.footer_info or _default_info

        env.globals["header_info"] = partial(header_info, app)
        env.globals["footer_info"] = partial(footer_info, app)
        env.globals["header_info_new_line"] = custom_jinja.header_info_new_line

        self.env = env

    def render(self, template_name: str, data=None) -> HTMLResponse:
        if not data:
            data = {}
        html_content = self.env.get_template(template_name).render(data)
        return HTMLResponse(content=html_content, status_code=200)
