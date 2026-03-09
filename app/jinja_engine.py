from datetime import datetime
from pathlib import Path

from babel.dates import format_datetime
from jinja2.environment import Environment
from jinja2.loaders import FileSystemLoader
from litestar.contrib.jinja import JinjaTemplateEngine

from app.config import user_roles, task_priority_name, task_priority_color, roles_access


def datetimeformat(date: str, format: str = "d MMMM y, HH:mm") -> str:
    dt = datetime.fromisoformat(date.replace("Z", "+00:00"))
    return format_datetime(dt, format=format, locale="ru")


def userrole(role: int) -> str:
    try:
        return user_roles[role]
    except KeyError:
        return '---'


def taskpriorityname(priority: int) -> str:
    try:
        return task_priority_name[priority]
    except KeyError:
        return '---'


def taskprioritycolor(priority: int) -> str:
    try:
        return task_priority_color[priority]
    except KeyError:
        return '#000000'


def issufficientrole(role: int, req_role: str) -> bool:
    if role >= roles_access[req_role]:
        return True
    else:
        return False


def get_jinja_engine(
    directory: Path | list[Path]
) -> JinjaTemplateEngine:
    jinja_env = Environment(
        loader=FileSystemLoader(directory),
        autoescape=True
    )
    jinja_env.filters["datetimeformat"] = datetimeformat
    jinja_env.filters["userrole"] = userrole
    jinja_env.filters["taskpriorityname"] = taskpriorityname
    jinja_env.filters["taskprioritycolor"] = taskprioritycolor
    jinja_env.filters["issufficientrole"] = issufficientrole
    return JinjaTemplateEngine(
        engine_instance=jinja_env
    )
