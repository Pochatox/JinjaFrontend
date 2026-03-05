import logging
from contextlib import asynccontextmanager
from typing import AsyncIterator

from litestar import Litestar, Request, exceptions, get
from litestar.di import Provide
from litestar.response import Redirect, Template
from litestar.template.config import TemplateConfig

from app.config import (SERVICE_NAME, HttpClient, HttpClientConfigDict,
                        HttpClientConfigType, cors_config, logging_config,
                        static_files_config, templates_path)
from app.handlers.auth import AuthController
from app.handlers.board import BoardController
from app.handlers.core import CoreController
from app.handlers.user import UserController
from app.http.clients import BaseAsyncHTTPClient
from app.jinja_engine import get_jinja_engine

logger = logging.getLogger('app.main')


@asynccontextmanager
async def lifespan(app: Litestar) -> AsyncIterator[None]:  # noqa: WPS213
    app.state.http_client = HttpClient(
        HttpClientConfigType(
            **HttpClientConfigDict,
            handler403=handler403,
            handler_login=handler_login,
            handler404=handler404
        )
    )
    await app.state.http_client.connect()

    logger.info(f'{SERVICE_NAME}: App started')
    yield

    await app.state.http_client.close()


def provide_http_client() -> BaseAsyncHTTPClient:
    return app.state.http_client


def handler_login() -> Redirect:
    return Redirect("/auth/login")


def handler403() -> Redirect:
    return Redirect("/403")


def handler404() -> Redirect:
    return Redirect("/404")


def handler5xx() -> Redirect:
    return Redirect('/5xx')


def exc_handler(request: Request, exc: Exception) -> Redirect:
    if isinstance(exc, exceptions.http_exceptions.NotFoundException):
        return handler404()
    logger.critical("Unhandled exception", exc_info=exc)
    return handler5xx()


@get("/5xx", sync_to_thread=False)
def get5xx() -> Template:
    return Template('5xx.html')


@get("/403", sync_to_thread=False)
def get403() -> Template:
    return Template('403.html')


@get("/404", sync_to_thread=False)
def get404() -> Template:
    return Template('404.html')


app = Litestar(
    lifespan=[lifespan],
    route_handlers=[
        CoreController,
        AuthController,
        UserController,
        BoardController,
        get403,
        get404,
        get5xx
    ],
    dependencies={
        'http_client': Provide(provide_http_client, sync_to_thread=False)
    },
    exception_handlers={
        Exception: exc_handler
    },
    template_config=TemplateConfig(
        engine=get_jinja_engine(templates_path),
    ),
    cors_config=cors_config,
    logging_config=logging_config,
    static_files_config=static_files_config,
    debug=True
)
