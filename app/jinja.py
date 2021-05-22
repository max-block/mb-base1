from markupsafe import Markup

from app.app import App
from app.models import DataStatus
from mb_base1.jinja import CustomJinja


def data_status(status: DataStatus):
    color = "black"
    if status == DataStatus.OK:
        color = "green"
    elif status == DataStatus.ERROR:
        color = "red"
    return Markup(f"<span style='color: {color};'>{status.value}</span>")


def header_info(_app: App):
    info = ""
    return Markup(info)


def footer_info(_app: App):
    info = ""
    return Markup(info)


custom_jinja = CustomJinja(header_info=header_info, footer_info=footer_info, filters={"data_status": data_status})
