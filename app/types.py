from typing import Any, Mapping, MutableMapping, TypeAlias

from litestar.response import Redirect

Sentinel: Any = object

AccessToken: TypeAlias = str
RefreshToken: TypeAlias = str

HeadersType: TypeAlias = MutableMapping[str, str]
HttpContent: TypeAlias = Mapping[str, Any]
HttpParams: TypeAlias = Mapping[str, str | int | float | bool]
HttpCookies: TypeAlias = dict[str, str]

HttpClientRedirect: TypeAlias = Redirect
