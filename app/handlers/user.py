# flake8-in-file-ignores: noqa: WPS432
# pyright: reportReturnType=false
# pyright: reportArgumentType=false
# pyright: reportAttributeAccessIssue=false

from litestar import Request, get
from litestar.exceptions.http_exceptions import NotFoundException
from litestar.response import Redirect, Template

from app.config import HttpClient, UserConfig
from app.handlers.controller import BaseController, HttpResponseStatuses


class UserController(BaseController[UserConfig]):
    config = UserConfig()
    path = '/user'

    @get("/id/{user_id:str}", name="user_by_id")
    async def user_page_by_id(
        self, request: Request, http_client: HttpClient, user_id: str
    ) -> Template | Redirect:
        http_status, httpx_response = await self.request(
            http_client=http_client,
            request=request,
            method='get',
            path=f'/user/id/{user_id}',
            expected_error_statuses=[400, 422]
        )
        if http_status == HttpResponseStatuses.REDIRECT:
            return httpx_response
        elif httpx_response.status_code == 200:
            return Template(
                "users/user.html",
                context={"user": httpx_response.json()}
            )
        else:
            raise NotFoundException

    @get("/username/{username:str}", name="user_by_username")
    async def user_page_by_username(
        self, request: Request, http_client: HttpClient, username: str
    ) -> Template | Redirect:
        http_status, httpx_response = await self.request(
            http_client=http_client,
            request=request,
            method='get',
            path=f'/user/username/{username}',
            expected_error_statuses=[422]
        )
        if http_status == HttpResponseStatuses.REDIRECT:
            return httpx_response
        elif httpx_response.status_code == 200:
            return Template(
                "users/user.html",
                context={"user": httpx_response.json()}
            )
        else:
            raise NotFoundException

    @get("/me", name="user_me")
    async def user_me(
        self, request: Request, http_client: HttpClient
    ) -> Template | Redirect:
        http_status, httpx_response = await self.request(
            http_client=http_client,
            request=request,
            method='get',
            path='/user/me'
        )
        if http_status == HttpResponseStatuses.REDIRECT:
            return httpx_response
        elif httpx_response.status_code == 200:
            return Template(
                "users/user.html",
                context={"user": httpx_response.json()}
            )
        else:
            raise NotFoundException

    @get("/invite/{token:str}", name="invite")
    async def invite(
        self, request: Request, http_client: HttpClient, token: str
    ) -> Template | Redirect:
        http_status, httpx_response = await self.request(
            http_client=http_client,
            request=request,
            method='get',
            path=f'/user/invite/{token}'
        )
        if http_status == HttpResponseStatuses.REDIRECT:
            return httpx_response
        elif httpx_response.status_code == 200:
            return Redirect('/')
        else:
            return Template(
                "5xx.html"
            )
