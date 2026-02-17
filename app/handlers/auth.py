# flake8-in-file-ignores: noqa: WPS432

from httpx import Response as Httpx_Response
from litestar import Request, Response, get, post
from litestar.response import Redirect, Template

from app.config import AuthConfig, HttpClient
from app.handlers.controller import BaseController, HttpResponseStatuses


class AuthController(BaseController[AuthConfig]):
    config = AuthConfig()
    path = '/auth'

    def set_auth_tokens(
        self, response: Response, httpx_response: Httpx_Response
    ) -> Response:
        response.set_cookie(
            key="access_token",
            value=httpx_response.headers.get('X-New-Access-Token'),
            httponly=True,
            secure=True,
            samesite="strict",
            max_age=self.config.max_tokens_age,
            path="/"
        )
        response.set_cookie(
            key="refresh_token",
            value=httpx_response.headers.get('X-New-Refresh-Token'),
            httponly=True,
            secure=True,
            samesite="strict",
            max_age=self.config.max_tokens_age,
            path=self.config.refresh_path
        )
        return response

    @get("/login", name="login")
    async def login_page(self) -> Template:
        return Template("auth/login.html")

    @post("/login")
    async def login_submit(
        self, request: Request, http_client: HttpClient
    ) -> Template | Redirect:
        form = await request.form()
        http_status, httpx_response = await self.request(
            http_client=http_client,
            request=request,
            method='post',
            path='/auth',
            json={
                "username": form.get("username"),
                "password": form.get("password")
            },
            expected_error_statuses=[401],
            update_tokens=False
        )
        if http_status == HttpResponseStatuses.REDIRECT:
            return httpx_response
        elif httpx_response.status_code == 201:
            response = self.set_auth_tokens(Redirect('/users/projects'), httpx_response)
            return response
        else:
            return Template(
                "auth/login.html",
                context={"error": self.get_error(httpx_response)}
            )

    @get("/registration", name="registration")
    async def registration_page(self) -> Template:
        return Template("auth/registration.html")

    @post("/registration")
    async def registration_submit(
        self, request: Request, http_client: HttpClient
    ) -> Template | Redirect:
        form = await request.form()
        http_status, httpx_response = await self.request(
            http_client=http_client,
            request=request,
            method='post',
            path='/auth/registration',
            json={
                "username": form.get("username"),
                "email": form.get("email"),
                "password": form.get("password"),
                "first_name": form.get("first_name"),
                "last_name": form.get("last_name"),
                "avatar": '',
            },
            expected_error_statuses=[409, 422],
            update_tokens=False
        )
        if http_status == HttpResponseStatuses.REDIRECT:
            return httpx_response
        elif httpx_response.status_code == 201:
            return Template("auth/registration_to_email.html")
        else:
            return Template(
                "auth/registration.html",
                context={"error": self.get_error(httpx_response)}
            )
