# flake8-in-file-ignores: noqa: WPS432
# pyright: reportReturnType=false
# pyright: reportArgumentType=false
# pyright: reportAttributeAccessIssue=false

from litestar import Request, get
from litestar.exceptions.http_exceptions import NotFoundException
from litestar.response import Redirect, Template

from app.config import HttpClient, CoreConfig
from app.handlers.controller import BaseController, HttpResponseStatuses


class CoreController(BaseController[CoreConfig]):
    config = CoreConfig()
    path = '/'

    @get("/", name="boards")
    async def users_boards(
        self, request: Request, http_client: HttpClient
    ) -> Template | Redirect:
        http_status, httpx_response = await self.request(
            http_client=http_client,
            request=request,
            method='get',
            path='/user/boards'
        )
        if http_status == HttpResponseStatuses.REDIRECT:
            return httpx_response
        elif httpx_response.status_code == 200:
            return Template(
                "boards/boards.html",
                context={"boards": httpx_response.json()['boards']}
            )
        else:
            raise NotFoundException
