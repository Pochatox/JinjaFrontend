# pyright: reportReturnType=false
# pyright: reportArgumentType=false
# pyright: reportAttributeAccessIssue=false

from litestar import Request, get, post
from litestar.exceptions.http_exceptions import HTTPException, NotFoundException
from litestar.response import Redirect, Template

from app.config import BoardConfig, HttpClient
from app.handlers.controller import BaseController, HttpResponseStatuses


class BoardController(BaseController[BoardConfig]):
    config = BoardConfig()
    path = '/board'

    @get('/{board_id:str}', name='get_board')
    async def get_board(
        self, request: Request, http_client: HttpClient, board_id: str
    ) -> Template | Redirect:
        http_status, httpx_response = await self.request(
            http_client=http_client,
            request=request,
            method='get',
            path=f'/board/{board_id}',
            expected_error_statuses=[422]
        )
        if http_status == HttpResponseStatuses.REDIRECT:
            return httpx_response
        if httpx_response.status_code == 200:
            response = Template(
                "boards/board.html",
                context={"board": httpx_response.json()}
            )
            if http_status == HttpResponseStatuses.NEW_TOKENS:
                response = self.set_tokens(response, httpx_response)
            return response
        else:
            raise NotFoundException

    @get('/column/{board_id:str}', name='get_column')
    async def get_column(
        self, request: Request, http_client: HttpClient, column_id: str
    ) -> Template | Redirect:
        http_status, httpx_response = await self.request(
            http_client=http_client,
            request=request,
            method='get',
            path=f'/column/{column_id}',
            expected_error_statuses=[422]
        )
        if http_status == HttpResponseStatuses.REDIRECT:
            return httpx_response
        if httpx_response.status_code == 200:
            response = Template(
                "boards/column.html",
                context={"column": httpx_response.json()}
            )
            if http_status == HttpResponseStatuses.NEW_TOKENS:
                response = self.set_tokens(response, httpx_response)
            return response
        else:
            raise NotFoundException

    @post("/", name='create_board')
    async def create_board(
        self, request: Request, http_client: HttpClient
    ) -> Template | Redirect:
        form = await request.form()
        http_status, httpx_response = await self.request(
            http_client=http_client,
            request=request,
            method='post',
            path='/board',
            json={
                "name": form.get("boardName"),
                "description": form.get("boardDescription")
            }
        )
        if http_status == HttpResponseStatuses.REDIRECT:
            return httpx_response
        if httpx_response.status_code == 201:
            response = Template(
                "boards/board.html",
                context={"board": httpx_response.json()}
            )
            if http_status == HttpResponseStatuses.NEW_TOKENS:
                response = self.set_tokens(response, httpx_response)
            return response
        else:
            raise HTTPException
