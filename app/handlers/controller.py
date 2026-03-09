# flake8-in-file-ignores: noqa: WPS110, WPS115
# pyright: reportReturnType=false
# pyright: reportArgumentType=false
# pyright: reportAttributeAccessIssue=false
import jwt
from enum import Enum
from typing import Generic, Sequence, TypeVar

from httpx import Response as Httpx_Response
from litestar import Request
from litestar.controller import Controller
from litestar.exceptions.http_exceptions import HTTPException
from litestar.response import Response
from typing_extensions import Literal

from app.config import BaseConfig, HttpClient
from app.http.clients import BaseAsyncHTTPClient
from app.types import (HeadersType, HttpClientRedirect, HttpContent,
                       HttpCookies, HttpParams, Sentinel)

ConfigType = TypeVar('ConfigType', bound=BaseConfig)


class HttpResponseStatuses(Enum):
    RESPONSE = 0
    NEW_TOKENS = 1
    REDIRECT = 2


class BaseController(Controller, Generic[ConfigType]):
    config: ConfigType
    path: str

    async def request(
        self, http_client: BaseAsyncHTTPClient, request: Request,
        method: str, path: str, params: HttpParams = Sentinel,
        json: HttpContent = Sentinel, add_headers: HeadersType = Sentinel,
        headers: HeadersType = Sentinel, cookies: HttpCookies = Sentinel,
        max_reconnections: int = Sentinel, timeout: float = Sentinel,
        header_auth_format: str = Sentinel,
        expected_error_statuses: Sequence = Sentinel, update_tokens: bool = True
    ) -> (
        tuple[Literal[HttpResponseStatuses.RESPONSE], Httpx_Response]
        | tuple[Literal[HttpResponseStatuses.NEW_TOKENS], Httpx_Response]
        | tuple[Literal[HttpResponseStatuses.REDIRECT], HttpClientRedirect]
    ):
        httpx_response = await http_client.request(
            method=method,
            path=path,
            access_token=request.cookies.get("access_token"),
            refresh_token=request.cookies.get("refresh_token"),
            params=params,
            json=json,
            add_headers=add_headers,
            headers=headers,
            cookies=cookies,
            max_reconnections=max_reconnections,
            timeout=timeout,
            header_auth_format=header_auth_format,
            expected_error_statuses=expected_error_statuses,
            update_tokens=update_tokens
        )
        if isinstance(httpx_response, HttpClientRedirect):
            return (HttpResponseStatuses.REDIRECT, httpx_response)
        elif httpx_response.extensions.get('is_new_tokens'):
            return (HttpResponseStatuses.NEW_TOKENS, httpx_response)
        else:
            return (HttpResponseStatuses.RESPONSE, httpx_response)

    async def get_user_role(
        self, request: Request, http_client: HttpClient, board_id: str
    ) -> int:
        http_status, httpx_response = await self.request(
            http_client=http_client,
            request=request,
            method='get',
            path=f'/board/{board_id}/role'
        )
        if httpx_response.status_code == 200:
            return int(httpx_response.text)
        else:
            raise HTTPException

    async def get_user_role_by_task(
        self, request: Request, http_client: HttpClient, task_id: str
    ) -> int:
        http_status, httpx_response = await self.request(
            http_client=http_client,
            request=request,
            method='get',
            path=f'/board/{task_id}/role-by-task'
        )
        if httpx_response.status_code == 200:
            return int(httpx_response.text)
        else:
            raise HTTPException

    def set_tokens(
        self, response: Response, httpx_response: Httpx_Response
    ) -> Response:
        response.set_cookie(
            key="access_token",
            value=httpx_response.extensions.get('access_token'),
            httponly=True,
            secure=True,
            samesite="strict",
            max_age=self.config.max_tokens_age,
            path="/"
        )
        response.set_cookie(
            key="refresh_token",
            value=httpx_response.extensions.get('refresh_token'),
            httponly=True,
            secure=True,
            samesite="strict",
            max_age=self.config.max_tokens_age,
            path="/"
        )
        return response

    def get_error(self, httpx_response: Httpx_Response) -> str:
        return httpx_response.json()['extra']['message']

    def get_user_id(self, request: Request) -> str:
        return jwt.decode(
            request.cookies.get("access_token"), options={"verify_signature": False}
        ).get("sub")
