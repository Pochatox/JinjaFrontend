# flake8-in-file-ignores: noqa: WPS201

import logging
import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv
from litestar.config.cors import CORSConfig
from litestar.contrib.jinja import JinjaTemplateEngine
from litestar.logging import LoggingConfig
from litestar.static_files import StaticFilesConfig
from litestar.template.config import TemplateConfig

from app.http.clients import AsyncHTTPXClient
from app.http.configs import AsyncHTTPXClientConfig

SERVICE_NAME = 'Pochatox-Jinja'
VERSION = '0.0.0'


APP_PATH = Path(__file__).parent
ROOT_PATH = APP_PATH.parent


load_dotenv(ROOT_PATH / '.env')

cors_config = CORSConfig(
    allow_origins=os.getenv('ALLOW_ORIGINS').split(',')  # type: ignore
)

logging_config = LoggingConfig(
    root={
        'level': 'DEBUG',
        'handlers': ['file']
    },
    handlers={
        'file': {
            'class': 'logging.FileHandler',
            'filename': ROOT_PATH / f"{SERVICE_NAME}.log",
            'mode': 'w',
            'formatter': 'standard',
        }
    },
    formatters={
        'standard': {
            'format': ('%(name)s | %(levelname)s | %(asctime)s'
                       ' | %(module)s | %(funcName)s | %(message)s'),
            'datefmt': '%Y-%m-%d %H:%M:%S'
        }
    },
    log_exceptions='always',
)

template_config = TemplateConfig(
    directory=Path(__file__).parent / "templates",
    engine=JinjaTemplateEngine
)
static_files_config = [
    StaticFilesConfig(
        path="/static",
        directories=["app/static"],
    )
]


HttpClient = AsyncHTTPXClient
HttpClientConfigType = AsyncHTTPXClientConfig
HttpClientConfigDict = {
    'logger': logging.getLogger('http_client'),
    'base_url': os.getenv('API_URL'),
    'header_auth_format': 'Bearer: {}',
    'access_token_header': 'Authorization',
    'refresh_token_header': 'Refresh-Token',
    'refresh_path': '/auth/refresh',
    'timeout': 5,
    'max_reconnections': 3
}


@dataclass(frozen=True)
class BaseConfig:
    max_tokens_age: int = 60 * 60 * 24 * 7


@dataclass(frozen=True)
class AuthConfig(BaseConfig):
    ...


@dataclass(frozen=True)
class UserConfig(BaseConfig):
    ...


@dataclass(frozen=True)
class BoardConfig(BaseConfig):
    ...
