# pyright: reportReturnType=false
# pyright: reportArgumentType=false
# pyright: reportAttributeAccessIssue=false

from litestar import Request, get, post
from litestar.exceptions.http_exceptions import (HTTPException,
                                                 NotFoundException)
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
                context={
                    "board": httpx_response.json(),
                    "user_role": await self.get_user_role(
                        request, http_client, board_id
                    )
                }
            )
            if http_status == HttpResponseStatuses.NEW_TOKENS:
                response = self.set_tokens(response, httpx_response)
            return response
        else:
            raise NotFoundException

    @get('/column/{column_id:str}', name='get_column')
    async def get_column(
        self, request: Request, http_client: HttpClient, column_id: str
    ) -> Template | Redirect:
        http_status, httpx_response = await self.request(
            http_client=http_client,
            request=request,
            method='get',
            path=f'/board/column/{column_id}',
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
            board = httpx_response.json()
            response = Template(
                "boards/board.html",
                context={
                    "board": board,
                    "user_role": await self.get_user_role(
                        request, http_client, board['id']
                    )
                }
            )
            if http_status == HttpResponseStatuses.NEW_TOKENS:
                response = self.set_tokens(response, httpx_response)
            return response
        else:
            raise HTTPException

    @post("/task", name='create_task')
    async def create_task(
        self, request: Request, http_client: HttpClient
    ) -> Template | Redirect:
        form = await request.form()
        board_id = form.get("task_board_id")
        http_status, httpx_response = await self.request(
            http_client=http_client,
            request=request,
            method='post',
            path='/task',
            json={
                "board_id": board_id,
                "name": form.get("task_name"),
                "description": form.get("task_description", "").strip(),
                "priority": form.get("task_priority"),
                "labels": (
                    form.getall("task_labels")
                    if "task_labels" in form else []
                )
            }
        )
        if http_status == HttpResponseStatuses.REDIRECT:
            return httpx_response
        if httpx_response.status_code == 201:
            response = Template(
                "boards/task.html",
                context={
                    "task": httpx_response.json(),
                    "user_id": self.get_user_id(request),
                    "user_role": await self.get_user_role(
                        request, http_client, board_id
                    )
                }
            )
            if http_status == HttpResponseStatuses.NEW_TOKENS:
                response = self.set_tokens(response, httpx_response)
            return response
        else:
            raise HTTPException

    @post("/column", name='create_column')
    async def create_column(
        self, request: Request, http_client: HttpClient
    ) -> Template | Redirect:
        form = await request.form()
        http_status, httpx_response = await self.request(
            http_client=http_client,
            request=request,
            method='post',
            path='/board/column',
            json={
                "board_id": form.get("column_board_id"),
                "name": form.get("column_name"),
                "description": form.get("column_description", "").strip(),
                "wip": form.get("column_wip"),
                "position": form.get("position")
            }
        )
        if http_status == HttpResponseStatuses.REDIRECT:
            return httpx_response
        if httpx_response.status_code == 201:
            response = Template(
                "boards/column.html",
                context={"column": httpx_response.json()}
            )
            if http_status == HttpResponseStatuses.NEW_TOKENS:
                response = self.set_tokens(response, httpx_response)
            return response
        else:
            raise HTTPException

    @post("/label", name='create_label')
    async def create_label(
        self, request: Request, http_client: HttpClient
    ) -> Redirect:
        form = await request.form()
        board_id = form.get("label_board_id")
        http_status, httpx_response = await self.request(
            http_client=http_client,
            request=request,
            method='post',
            path='/board/label',
            json={
                "board_id": board_id,
                "name": form.get("label_name"),
                "color": form.get("label_color")
            }
        )
        if http_status == HttpResponseStatuses.REDIRECT:
            return httpx_response
        if httpx_response.status_code == 201:
            response = Redirect(f'/board/{board_id}')
            if http_status == HttpResponseStatuses.NEW_TOKENS:
                response = self.set_tokens(response, httpx_response)
            return response
        else:
            raise HTTPException

    @get('/task/{task_id:str}', name='get_task')
    async def get_task(
        self, request: Request, http_client: HttpClient, task_id: str
    ) -> Template | Redirect:
        http_status, httpx_response = await self.request(
            http_client=http_client,
            request=request,
            method='get',
            path=f'/task/{task_id}',
            expected_error_statuses=[422]
        )
        if http_status == HttpResponseStatuses.REDIRECT:
            return httpx_response
        if httpx_response.status_code == 200:
            response = Template(
                "boards/task.html",
                context={
                    "task": httpx_response.json(),
                    "user_id": self.get_user_id(request),
                    "user_role": await self.get_user_role_by_task(
                        request, http_client, task_id
                    )
                }
            )
            if http_status == HttpResponseStatuses.NEW_TOKENS:
                response = self.set_tokens(response, httpx_response)
            return response
        else:
            raise NotFoundException

    @get('/{board_id:str}/not-assigned-tasks', name='get_not_assigned_tasks')
    async def get_not_assigned_tasks(
        self, request: Request, http_client: HttpClient, board_id: str
    ) -> Template | Redirect:
        http_status, httpx_response = await self.request(
            http_client=http_client,
            request=request,
            method='get',
            path=f'/board/{board_id}/not-assigned-tasks'
        )
        if http_status == HttpResponseStatuses.REDIRECT:
            return httpx_response
        if httpx_response.status_code == 200:
            response = Template(
                "boards/tasks.html",
                context={
                    "state": "not_assigned",
                    "board_id": board_id,
                    "tasks": httpx_response.json()
                }
            )
            if http_status == HttpResponseStatuses.NEW_TOKENS:
                response = self.set_tokens(response, httpx_response)
            return response
        else:
            raise NotFoundException

    @get('/{board_id:str}/confirmed-tasks', name='get_confirmed_tasks')
    async def get_confirmed_tasks(
        self, request: Request, http_client: HttpClient, board_id: str
    ) -> Template | Redirect:
        http_status, httpx_response = await self.request(
            http_client=http_client,
            request=request,
            method='get',
            path=f'/board/{board_id}/confirmed-tasks'
        )
        if http_status == HttpResponseStatuses.REDIRECT:
            return httpx_response
        if httpx_response.status_code == 200:
            response = Template(
                "boards/tasks.html",
                context={
                    "state": "confirmed",
                    "board_id": board_id,
                    "tasks": httpx_response.json()
                }
            )
            if http_status == HttpResponseStatuses.NEW_TOKENS:
                response = self.set_tokens(response, httpx_response)
            return response
        else:
            raise NotFoundException

    @post('/task-assignee/{task_id:str}', name='task_assignee')
    async def task_assignee(
        self, request: Request, http_client: HttpClient, task_id: str
    ) -> Template | Redirect:
        http_status, httpx_response = await self.request(
            http_client=http_client,
            request=request,
            method='patch',
            path='/task/assignee',
            json={
                "task_id": task_id
            },
            expected_error_statuses=[409, 422]
        )
        if http_status == HttpResponseStatuses.REDIRECT:
            return httpx_response

        if httpx_response.status_code == 200:
            response = Redirect(f'/board/task/{task_id}')
            if http_status == HttpResponseStatuses.NEW_TOKENS:
                response = self.set_tokens(response, httpx_response)
            return response

        elif httpx_response.status_code == 409:
            http_status409, httpx_response409 = await self.request(
                http_client=http_client,
                request=request,
                method='get',
                path=f'/task/{task_id}'
            )
            response = Template(
                "boards/task.html",
                context={
                    "task": httpx_response409.json(),
                    "user_role": await self.get_user_role_by_task(
                        request, http_client, task_id
                    ),
                    "error": 409
                }
            )
            if http_status == HttpResponseStatuses.NEW_TOKENS:
                response = self.set_tokens(response, httpx_response)
            return response

        elif httpx_response.status_code == 422:
            http_status422, httpx_response422 = await self.request(
                http_client=http_client,
                request=request,
                method='get',
                path=f'/task/{task_id}'
            )
            response = Template(
                "boards/task.html",
                context={
                    "task": httpx_response422.json(),
                    "user_role": await self.get_user_role_by_task(
                        request, http_client, task_id
                    ),
                    "error": 422
                }
            )
            if http_status == HttpResponseStatuses.NEW_TOKENS:
                response = self.set_tokens(response, httpx_response)
            return response
        else:
            raise HTTPException

    @post('/task-confirm/{task_id:str}', name='task_confirm')
    async def task_confirm(
        self, request: Request, http_client: HttpClient, task_id: str
    ) -> Template | Redirect:
        http_status, httpx_response = await self.request(
            http_client=http_client,
            request=request,
            method='patch',
            path='/task/confirm',
            json={
                "task_id": task_id
            },
            expected_error_statuses=[409]
        )
        if http_status == HttpResponseStatuses.REDIRECT:
            return httpx_response

        if httpx_response.status_code == 200:
            response = Redirect(f'/board/task/{task_id}')
            if http_status == HttpResponseStatuses.NEW_TOKENS:
                response = self.set_tokens(response, httpx_response)
            return response

        elif httpx_response.status_code == 409:
            http_status409, httpx_response409 = await self.request(
                http_client=http_client,
                request=request,
                method='get',
                path=f'/task/{task_id}'
            )
            response = Template(
                "boards/task.html",
                context={
                    "task": httpx_response409.json(),
                    "error": 409,
                    "user_role": await self.get_user_role_by_task(
                        request, http_client, task_id
                    )
                }
            )
            if http_status == HttpResponseStatuses.NEW_TOKENS:
                response = self.set_tokens(response, httpx_response)
            return response

        else:
            raise HTTPException

    @post('/task/{task_id:str}/move-to/{column_position:int}', name='task_move_to')
    async def task_move_to(
        self, request: Request, http_client: HttpClient, task_id: str,
        column_position: int
    ) -> Template | Redirect:
        http_status, httpx_response = await self.request(
            http_client=http_client,
            request=request,
            method='patch',
            path='/task/move',
            json={
                "task_id": task_id,
                "move_to": column_position
            },
            expected_error_statuses=[409]
        )
        if http_status == HttpResponseStatuses.REDIRECT:
            return httpx_response

        if httpx_response.status_code == 200:
            response = Redirect(f'/board/task/{task_id}')
            if http_status == HttpResponseStatuses.NEW_TOKENS:
                response = self.set_tokens(response, httpx_response)
            return response

        elif httpx_response.status_code == 409:
            http_status409, httpx_response409 = await self.request(
                http_client=http_client,
                request=request,
                method='get',
                path=f'/task/{task_id}'
            )
            response = Template(
                "boards/task.html",
                context={
                    "task": httpx_response409.json(),
                    "error": 409,
                    "user_role": await self.get_user_role_by_task(
                        request, http_client, task_id
                    )
                }
            )
            if http_status == HttpResponseStatuses.NEW_TOKENS:
                response = self.set_tokens(response, httpx_response)
            return response

        else:
            raise HTTPException

    @get('/{board_id:str}/users-list', name='get_users_list')
    async def get_users_list(
        self, request: Request, http_client: HttpClient, board_id: str
    ) -> Template | Redirect:
        http_status, httpx_response = await self.request(
            http_client=http_client,
            request=request,
            method='get',
            path=f'/board/{board_id}/users-list'
        )
        if http_status == HttpResponseStatuses.REDIRECT:
            return httpx_response
        if httpx_response.status_code == 200:
            response = Template(
                "boards/userslist.html",
                context={
                    "board_users": httpx_response.json()
                }
            )
            if http_status == HttpResponseStatuses.NEW_TOKENS:
                response = self.set_tokens(response, httpx_response)
            return response
        else:
            raise NotFoundException

    @get('/{board_id:str}/task-transitions', name='get_task_transitions')
    async def get_task_transitions(
        self, request: Request, http_client: HttpClient, board_id: str
    ) -> Template | Redirect:
        http_status, httpx_response = await self.request(
            http_client=http_client,
            request=request,
            method='get',
            path=f'/board/{board_id}/task-transitions'
        )
        if http_status == HttpResponseStatuses.REDIRECT:
            return httpx_response
        if httpx_response.status_code == 200:
            response = Template(
                "boards/tasktransitions.html",
                context={
                    "history": httpx_response.json(),
                    "board_id": board_id
                }
            )
            if http_status == HttpResponseStatuses.NEW_TOKENS:
                response = self.set_tokens(response, httpx_response)
            return response
        else:
            raise NotFoundException

    @post('/task/{task_id:str}/comment', name='task_comment')
    async def create_comment(
        self, request: Request, http_client: HttpClient, task_id: str
    ) -> Template | Redirect:
        form = await request.form()
        http_status, httpx_response = await self.request(
            http_client=http_client,
            request=request,
            method='post',
            path='/task/comment',
            json={
                "task_id": task_id,
                "text": form.get('comment_text')
            }
        )
        if http_status == HttpResponseStatuses.REDIRECT:
            return httpx_response

        if httpx_response.status_code == 201:
            response = Redirect(f'/board/task/{task_id}')
            if http_status == HttpResponseStatuses.NEW_TOKENS:
                response = self.set_tokens(response, httpx_response)
            return response

        else:
            raise HTTPException

    @get('/{board_id:str}/management', name='get_board_management')
    async def get_board_management(
        self, request: Request, http_client: HttpClient, board_id: str
    ) -> Template | Redirect:
        http_status, httpx_response = await self.request(
            http_client=http_client,
            request=request,
            method='get',
            path=f'/board/{board_id}/users-list'
        )
        if http_status == HttpResponseStatuses.REDIRECT:
            return httpx_response
        if httpx_response.status_code == 200:
            response = Template(
                "boards/management.html",
                context={
                    "board_users": httpx_response.json(),
                    "user_role": await self.get_user_role(
                        request, http_client, board_id
                    )
                }
            )
            if http_status == HttpResponseStatuses.NEW_TOKENS:
                response = self.set_tokens(response, httpx_response)
            return response
        else:
            raise NotFoundException

    @post('/{board_id:str}/invite', name='invite_request')
    async def invite_request(
        self, request: Request, http_client: HttpClient, board_id: str
    ) -> Template | Redirect:
        form = await request.form()
        http_status, httpx_response = await self.request(
            http_client=http_client,
            request=request,
            method='post',
            path='/user/invite-request',
            json={
                "invited_username": form.get('invited_username'),
                "board_id": board_id
            },
            expected_error_statuses=[403, 409, 422]
        )
        if http_status == HttpResponseStatuses.REDIRECT:
            return httpx_response

        if httpx_response.status_code == 201:
            response = Redirect(f'/board/{board_id}/user-list')
            if http_status == HttpResponseStatuses.NEW_TOKENS:
                response = self.set_tokens(response, httpx_response)
            return response
        else:
            http_status_e, httpx_response_e = await self.request(
                http_client=http_client,
                request=request,
                method='get',
                path=f'/board/{board_id}/users-list'
            )
            if http_status_e == HttpResponseStatuses.REDIRECT:
                return httpx_response_e
            else:
                return Template(
                    "boards/management.html",
                    context={
                        "board_users": httpx_response_e.json(),
                        "user_role": await self.get_user_role(
                            request, http_client, board_id
                        ),
                        "error": self.get_error(httpx_response)
                    }
                )

    @post('/{board_id:str}/delete_user', name='delete_user')
    async def delete_user(
        self, request: Request, http_client: HttpClient, board_id: str
    ) -> Template | Redirect:
        form = await request.form()
        user_id = form.get('removed_username')
        http_status, httpx_response = await self.request(
            http_client=http_client,
            request=request,
            method='delete',
            path='/board/user',
            json={
                "user_id": user_id,
                "board_id": board_id
            },
            expected_error_statuses=[403, 409, 422]
        )

        if http_status == HttpResponseStatuses.REDIRECT:
            return httpx_response

        if httpx_response.status_code == 204:
            response = Redirect(f'/board/{board_id}/user-list')
            if http_status == HttpResponseStatuses.NEW_TOKENS:
                response = self.set_tokens(response, httpx_response)
            return response

        else:
            http_status_e, httpx_response_e = await self.request(
                http_client=http_client,
                request=request,
                method='get',
                path=f'/board/{board_id}/users-list'
            )
            return Template(
                "boards/management.html",
                context={
                    "error": self.get_error(httpx_response),
                    "board_users": httpx_response_e.json(),
                    "user_role": await self.get_user_role(
                        request, http_client, board_id
                    )
                }
            )

    @post('/{board_id:str}/maintainer', name='create_maintainer')
    async def create_maintainer(
        self, request: Request, http_client: HttpClient, board_id: str
    ) -> Template | Redirect:
        form = await request.form()
        user_id = form.get('user_id')
        http_status, httpx_response = await self.request(
            http_client=http_client,
            request=request,
            method='post',
            path=f'/board/{board_id}/maintainer',
            json={
                "maintainer_id": user_id,
            },
            expected_error_statuses=[403, 409, 422]
        )

        if http_status == HttpResponseStatuses.REDIRECT:
            return httpx_response

        if httpx_response.status_code in (200, 201):
            response = Redirect(f'/board/{board_id}/user-list')
            if http_status == HttpResponseStatuses.NEW_TOKENS:
                response = self.set_tokens(response, httpx_response)
            return response

        else:
            http_status_e, httpx_response_e = await self.request(
                http_client=http_client,
                request=request,
                method='get',
                path=f'/board/{board_id}/users-list'
            )
            return Template(
                "boards/management.html",
                context={
                    "error": self.get_error(httpx_response),
                    "board_users": httpx_response_e.json(),
                    "user_role": await self.get_user_role(
                        request, http_client, board_id
                    )
                }
            )
