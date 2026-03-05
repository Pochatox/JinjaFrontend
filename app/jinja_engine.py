from datetime import datetime
from pathlib import Path

from babel.dates import format_datetime
from jinja2.environment import Environment
from jinja2.loaders import FileSystemLoader
from litestar.contrib.jinja import JinjaTemplateEngine

from app.config import user_roles


def datetimeformat(date: str, format: str = "d MMMM y, HH:mm") -> str:
    dt = datetime.fromisoformat(date.replace("Z", "+00:00"))
    return format_datetime(dt, format=format, locale="ru")


def userrole(role: int) -> str:
    try:
        return user_roles[role]
    except KeyError:
        return '---'


def get_jinja_engine(
    directory: Path | list[Path]
) -> JinjaTemplateEngine:
    jinja_env = Environment(
        loader=FileSystemLoader(directory),
        autoescape=True
    )
    jinja_env.filters["datetimeformat"] = datetimeformat
    jinja_env.filters["userrole"] = userrole
    return JinjaTemplateEngine(
        engine_instance=jinja_env
    )
