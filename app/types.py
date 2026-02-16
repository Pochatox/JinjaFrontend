from typing import Any, Mapping, TypeAlias

from litestar.response import Redirect

Sentinel: Any = object

AccessToken: TypeAlias = str
RefreshToken: TypeAlias = str

HeadersType: TypeAlias = Mapping[str, str]
HttpContent: TypeAlias = Mapping[str, Any]
HttpParams: TypeAlias = Mapping[str, str | int | float | bool]
HttpCookies: TypeAlias = Mapping[str, str]

HttpClientRedirect: TypeAlias = Redirect
