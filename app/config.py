# flake8-in-file-ignores: noqa: WPS201

import logging
import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv
from litestar.config.cors import CORSConfig
from litestar.logging import LoggingConfig
from litestar.static_files import StaticFilesConfig

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


templates_path = Path(__file__).parent / "templates"

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
class CoreConfig(BaseConfig):
    ...


@dataclass(frozen=True)
class AuthConfig(BaseConfig):
    ...


@dataclass(frozen=True)
class UserConfig(BaseConfig):
    ...


@dataclass(frozen=True)
class BoardConfig(BaseConfig):
    ...


avatars = [
    "artichoke.png",
    "asparagus.png",
    "bean.png",
    "beetroot.png",
    "bell_pepper.png",
    "black_radish.png",
    "broccoli.png",
    "carrot.png",
    "cauliflower.png",
    "celery.png",
    "corn.png",
    "cucumber.png",
    "dill.png",
    "eggplant.png",
    "garlic.png",
    "grean_pees.png",
    "horseradish.png",
    "jerusalem.png",
    "Kohlabi.png",
    "leaf_lettuce.png",
    "leek.png",
    "napa_cabbage.png",
    "onion.png",
    "parsley.png",
    "parsnip.png",
    "pattypan_squash.png",
    "pod_of_peas.png",
    "pumpkin.png",
    "radish.png",
    "rutabaga.png",
    "shallot.png",
    "sorrel.png",
    "spinach.png",
    "sweet_potato.png",
    "tomato.png",
    "turnip.png",
    "white_cabbage.png",
    "zucchini.png",
]


user_roles = {
    10: 'Пользователь',
    50: 'Лидер команды',
    100: 'Владелец'
}


task_priority_name = {
    10: 'низкий',
    20: 'средний',
    30: 'высокий',
    40: 'очень высоко',
    50: 'КРИТИЧНО'
}


task_priority_color = {
    10: '#b8e994',
    20: '#d8f5a2',
    30: '#fff3b0',
    40: '#ffd8a8',
    50: '#ffa8a8'
}


roles_access = {
    'min_invite_role': 100,
    'min_delete_user_role': 100,
    'min_create_column_role': 100,
    'min_create_maintainer_role': 100,
    'min_create_task_role': 50,
    'min_confirm_task_role': 50,
    'min_task_transitions_role': 10,
    'min_create_label_role': 10,
    'min_check_task_role': 10,
    'min_assignee_task_role': 10
}
