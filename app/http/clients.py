# flake8-in-file-ignores: noqa: WPS110, WPS432, E129, E731

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import (Awaitable, Callable, Generic, Optional, Self, Sequence,
                    TypeVar)

from httpx import AsyncClient, ConnectError, Response

from app import errors
from app.http.configs import AsyncHTTPXClientConfig, BaseAsyncHTTPClientConfig
from app.types import (AccessToken, HeadersType, HttpClientRedirect,
                       HttpContent, HttpCookies, HttpParams, RefreshToken,
                       Sentinel)

HTTPConfig = TypeVar('HTTPConfig', bound=BaseAsyncHTTPClientConfig)


@dataclass
class BaseAsyncHTTPClient(ABC, Generic[HTTPConfig]):
    config: HTTPConfig
    client: AsyncClient | None = field(init=False, default=None)

    @abstractmethod
    async def connect(self) -> Self: ...

    @abstractmethod
    async def close(self) -> None: ...

    @abstractmethod
    async def request(
        self, method: str, path: str, access_token: Optional[AccessToken] = None,
        refresh_token: Optional[RefreshToken] = None, params: HttpParams = Sentinel,
        json: HttpContent = Sentinel, add_headers: HeadersType = Sentinel,
        headers: HeadersType = Sentinel, cookies: HttpCookies = Sentinel,
        max_reconnections: int = Sentinel, timeout: float = Sentinel,
        header_auth_format: str = Sentinel,
        expected_error_statuses: Sequence = Sentinel, _recursion: bool = False
    ) -> Response | HttpClientRedirect: ...


@dataclass
class AsyncHTTPXClient(BaseAsyncHTTPClient[AsyncHTTPXClientConfig]):

    async def connect(self) -> Self:
        self.client = AsyncClient(
            base_url=self.config.base_url,
            timeout=self.config.timeout
        )
        self.config.logger.info('HTTPX: connect')
        return self

    async def request(
        self, method: str, path: str, access_token: Optional[AccessToken] = None,
        refresh_token: Optional[RefreshToken] = None, params: HttpParams = Sentinel,
        json: HttpContent = Sentinel, add_headers: HeadersType = Sentinel,
        headers: HeadersType = Sentinel, cookies: HttpCookies = Sentinel,
        max_reconnections: int = Sentinel, timeout: float = Sentinel,
        header_auth_format: str = Sentinel,
        expected_error_statuses: Sequence = Sentinel, update_tokens: bool = False
    ) -> Response | HttpClientRedirect:
        timeout = self.config.timeout if timeout is Sentinel else timeout
        if timeout < 0:
            raise ValueError('the timeout cannot be less than 0')

        max_reconnections = (
            self.config.max_reconnections if max_reconnections is Sentinel
            else max_reconnections
        )
        if max_reconnections < 1:
            raise ValueError('the max_reconnections cannot be less than 1')

        if add_headers is not Sentinel and headers is not Sentinel:
            raise ValueError('Cannot use both "headers" and "add_headers": '
                             '"headers" replaces auto-generated headers,'
                             ' while "add_headers" appends to them.')

        header_auth_format = (
            self.config.header_auth_format if header_auth_format is Sentinel
            else header_auth_format
        )

        if headers is Sentinel:
            if add_headers is not Sentinel:
                headers = add_headers
            else:
                headers = {}

            if access_token:
                headers[self.config.access_token_header] = header_auth_format.format(
                    access_token
                )
            if refresh_token:
                headers[self.config.refresh_token_header] = refresh_token

        url = self.config.base_url + path

        for reconnections in range(1, max_reconnections + 1, 1):  # noqa: B007
            try:
                httpx_response = await self.client.request(
                    method=method,
                    url=url,
                    json=json if json is not Sentinel else None,
                    params=params if params is not Sentinel else None,
                    headers=headers,
                    cookies=cookies if cookies is not Sentinel else None,
                    timeout=timeout
                )
                break

            except ConnectError:
                self.config.logger.warning(f"{url} did not respond")

            if reconnections == max_reconnections:
                msg = (
                    f'{url} did not respond {max_reconnections} '
                    f'times (timeout {timeout})'
                )
                self.config.logger.critical(msg)
                raise ConnectionError(msg)

        if (httpx_response.status_code < 300
            or expected_error_statuses is not Sentinel
            and httpx_response.status_code in expected_error_statuses):
            return httpx_response

        if httpx_response.status_code >= 500:
            msg = f"{url} responded with {httpx_response.status_code}"
            self.config.logger.critical(msg)
            raise ConnectionError(msg)

        elif httpx_response.status_code == 404:
            self.config.logger.debug(f'{url} - {httpx_response.status_code}')
            return await self.config.handler404()

        elif httpx_response.status_code == 401 and update_tokens:
            try:
                error_code = httpx_response.json()['extra']['error_code']
            except KeyError as e:
                raise ConnectionError from e

            if error_code in [
                errors.AccessTokenInvalid, errors.AuthorizationHeaderMissing
            ]:
                return self.config.handler_login()

            elif error_code == errors.AccessTokenExpired:
                self_recursion = lambda a_t, r_t: self.request(
                    method=method,
                    path=path,
                    access_token=a_t,
                    refresh_token=r_t,
                    params=params,
                    content=json,
                    add_headers=add_headers,
                    headers=headers,
                    cookies=cookies,
                    max_reconnections=max_reconnections,
                    timeout=timeout,
                    header_auth_format=header_auth_format,
                    expected_error_statuses=expected_error_statuses,
                    update_tokens=False
                )
                return await self._update_tokens(
                    access_token=access_token,
                    refresh_token=refresh_token,
                    await_after=self_recursion
                )

        else:
            self.config.logger.critical(
                f'{url} - {httpx_response.status_code} '
                '- Unsuccessful attempt to take tokens'
            )
            raise ConnectionError('Unsuccessful attempt to take tokens')

    async def close(self) -> None:
        await self.client.aclose()
        self.config.logger.info('HTTPX: close')

    async def _update_tokens(
        self, access_token: AccessToken, refresh_token: RefreshToken,
        await_after: Callable[[AccessToken, RefreshToken], Awaitable[Response]]
    ) -> Response | HttpClientRedirect:
        url = self.config.base_url + self.config.refresh_path
        httpx_response = await self.client.get(
            url=url,
            headers={
                self.config.access_token_header: self.config.header_auth_format.format(
                    access_token
                ),
                self.config.refresh_token_header: refresh_token
            }
        )
        self.config.logger.debug(f'{url} - {httpx_response.status_code}')
        if httpx_response.status_code < 300:
            new_access_token = httpx_response.headers['X-New-Access-Token']
            new_refresh_token = httpx_response.headers['X-New-Refresh-Token']
            response = await await_after(
                new_access_token,
                new_refresh_token
            )
            response.extensions['is_new_tokens'] = True
            response.extensions['new_access_token'] = new_access_token
            response.extensions['new_refresh_token'] = new_refresh_token
            return response
        else:
            return self.config.handler_login()
