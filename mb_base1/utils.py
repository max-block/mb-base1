from fastapi import Depends
from starlette.requests import Request
from starlette.responses import PlainTextResponse, RedirectResponse
from starlette.status import HTTP_303_SEE_OTHER


async def get_form_data(request: Request):
    return await request.form()


depends_form = Depends(get_form_data)


def plain_text(content) -> PlainTextResponse:
    return PlainTextResponse(content)


def redirect(url: str) -> RedirectResponse:
    return RedirectResponse(url, status_code=HTTP_303_SEE_OTHER)


def get_registered_attributes(dconfig):
    return [x for x in dir(dconfig) if not x.startswith("_")]
