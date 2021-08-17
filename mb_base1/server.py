import json
import traceback
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Optional

from fastapi import APIRouter, Depends, FastAPI, Form, HTTPException, Security
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.openapi.models import APIKey
from fastapi.openapi.utils import get_openapi
from fastapi.security import APIKeyCookie, APIKeyHeader, APIKeyQuery
from mb_commons import hrequest
from starlette import status
from starlette.requests import Request
from starlette.responses import JSONResponse, PlainTextResponse, RedirectResponse
from starlette.staticfiles import StaticFiles
from starlette.status import HTTP_403_FORBIDDEN

from mb_base1.app import BaseApp
from mb_base1.errors import UserError
from mb_base1.jinja import Templates
from mb_base1.routers import base_ui_router, dconfig_router, dlog_router, dvalue_router, system_router
from mb_base1.telegram import BaseTelegram


@dataclass
class AppRouter:
    router: APIRouter
    tag: str
    prefix: str = ""


class Server:
    api_key_name = "access-token"
    key_query = Security(APIKeyQuery(name=api_key_name, auto_error=False))
    key_header = Security(APIKeyHeader(name=api_key_name, auto_error=False))
    key_cookie = Security(APIKeyCookie(name=api_key_name, auto_error=False))

    def __init__(self, app: BaseApp, telegram: BaseTelegram, routers: list[AppRouter], templates: Templates):
        self.app = app
        self.telegram = telegram
        self.server = FastAPI(
            title=app.app_config.app_name,
            docs_url=None,
            redoc_url=None,
            openapi_url=None,
            openapi_tags=app.app_config.tags_metadata,
        )
        self.templates = templates
        self._configure_server()
        self._configure_openapi()
        self._configure_routers(routers)
        telegram.start()

    def get_server(self) -> FastAPI:
        return self.server

    def _configure_routers(self, routers: list[AppRouter]):
        base_routers = [
            AppRouter(dconfig_router.init(self.app), "dconfig", "/api/dconfigs"),
            AppRouter(dvalue_router.init(self.app), "dvalue", "/api/dvalues"),
            AppRouter(dlog_router.init(self.app), "dlog", "/api/dlogs"),
            AppRouter(system_router.init(self.app, self.telegram), "system", "/api/system"),
            AppRouter(base_ui_router.init(self.app, self.templates, self.telegram), "base-ui"),
        ]

        for r in base_routers + routers:
            self.server.include_router(
                r.router,
                prefix=r.prefix,
                dependencies=[Depends(self._get_api_key())],
                tags=[r.tag],
            )

    def _configure_server(self):
        @self.server.exception_handler(Exception)
        async def exception_handler(_request: Request, err: Exception):
            code = getattr(err, "code", None)

            message = str(err)

            hide_stacktrace = isinstance(err, UserError)
            if code in [400, 401, 403, 404, 405]:
                hide_stacktrace = True

            if not hide_stacktrace:
                self.app.logger.exception(err)
                message += "\n\n" + traceback.format_exc()

            if not self.app.app_config.debug:
                message = "error"

            return PlainTextResponse(message, status_code=500)

        @self.server.on_event("shutdown")
        def shutdown_server():
            self.app.logger.debug("server shutdown")
            self.telegram.stop()
            self.app.shutdown()

        current_dir = Path(__file__).parent.absolute()
        self.server.mount("/static", StaticFiles(directory=current_dir.joinpath("static")), name="static")

    def _configure_openapi(self):
        @self.server.get("/openapi.json", tags=["openapi"], include_in_schema=False)
        async def get_open_api_endpoint(_api_key: APIKey = Depends(self._get_api_key())):
            response = JSONResponse(
                get_openapi(
                    title=self.app.app_config.app_name,
                    version=self.app.app_config.app_version,
                    routes=self.server.routes,
                    tags=self.app.app_config.tags_metadata,
                ),
            )
            return response

        @self.server.get("/api", tags=["openapi"], include_in_schema=False)
        async def get_documentation(api_key: APIKey = Depends(self._get_api_key())):
            response = get_swagger_ui_html(openapi_url="/openapi.json", title=self.app.app_config.app_name)
            # noinspection PyTypeChecker
            response.set_cookie(
                self.api_key_name,
                value=api_key,
                domain=self.app.app_config.domain,
                httponly=True,
                max_age=60 * 60 * 24 * 30,
                expires=60 * 60 * 24 * 30,
            )
            return response

        @self.server.get("/login", tags=["auth"])
        async def route_login_page():
            return self.templates.render("login.j2")

        @self.server.post("/login", tags=["auth"])
        async def route_login_action(access_token: str = Form(...)):
            response = RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)
            response.set_cookie(
                self.api_key_name,
                value=access_token,
                domain=self.app.app_config.domain,
                httponly=True,
                max_age=60 * 60 * 24 * 30,
                expires=60 * 60 * 24 * 30,
            )
            return response

        @self.server.get("/logout", tags=["auth"])
        async def route_logout_and_remove_cookie():
            response = RedirectResponse(url="/")
            response.delete_cookie(self.api_key_name, domain=self.app.app_config.domain)
            return response

        @self.server.get("/api-link")
        def api_redirect(
            request: Request,
            url: str,
            method: str,
            data: Optional[str] = None,
            api_key: APIKey = Depends(self._get_api_key()),
        ):
            method = method.lower()
            headers = {self.api_key_name: api_key}
            url = str(request.base_url).removesuffix("/") + url
            if self.app.app_config.use_https:
                url = url.replace("http://", "https://", 1)

            params = None
            if data:
                params = json.loads(data)
            res = hrequest(url, method=method, headers=headers, params=params, json_params=True, timeout=600)
            if res.json:
                return res.json
            return res.body

    def _get_api_key(self) -> Callable:
        async def _get_api_key(
            query: str = Server.key_query,
            header: str = Server.key_header,
            cookie: str = Server.key_cookie,
        ):
            if query == self.app.app_config.access_token:
                return query
            elif header == self.app.app_config.access_token:
                return header
            elif cookie == self.app.app_config.access_token:
                return cookie
            else:
                raise HTTPException(status_code=HTTP_403_FORBIDDEN, detail="access denied")

        return _get_api_key
