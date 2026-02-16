import logging
from typing import Callable

from pydantic import BaseModel, Field

from app.types import HttpClientRedirect


class BaseAsyncHTTPClientConfig(BaseModel):
    logger: logging.Logger
    base_url: str
    header_auth_format: str
    access_token_header: str
    refresh_token_header: str
    handler_login: Callable[[], HttpClientRedirect]
    handler404: Callable[[], HttpClientRedirect]
    refresh_path: str
    timeout: float = Field(..., gt=0)
    max_reconnections: int = Field(..., ge=1)

    class Config:
        arbitrary_types_allowed = True


class AsyncHTTPXClientConfig(BaseAsyncHTTPClientConfig):
    ...
