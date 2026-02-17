from litestar import Request, get
from litestar.response import Redirect, Template

from app.config import HttpClient, BoardConfig
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
            path=f'/board/{board_id}'
        )
        if http_status == HttpResponseStatuses.REDIRECT:
            return httpx_response
        response = Template(
            "boards/board.html",
            context={"board": httpx_response.json()}
        )
        if http_status == HttpResponseStatuses.NEW_TOKENS:
            response = self.set_tokens(response, httpx_response)
        return response
