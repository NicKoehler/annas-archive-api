from time import time
from aiohttp import ClientSession
from dataclasses import dataclass
from sanic.request import Request
from sanic.response import HTTPResponse


@dataclass
class Response:
    status_code: int
    text: str


@dataclass
class Cache:
    response: HTTPResponse
    expires: float


async def get(url: str, params: dict = {}) -> Response:
    session = ClientSession()
    response = await session.get(url, params=params)
    text = await response.text()
    await session.close()
    return Response(response.status, text)


def cache(func):
    cache_storage: dict[str, Cache] = {}

    async def wrapper(request: Request, *args, **kwargs) -> HTTPResponse:
        cache_data = cache_storage.get(request.url)
        if not cache_data or cache_data.expires < time():
            response = await func(request, *args, **kwargs)
            cache_storage[request.url] = Cache(response, time() + 3600)
            cache_data = cache_storage[request.url]
        expires_in = cache_data.expires - time()
        cache_data.response.headers["Cache-Control"] = f"max-age={expires_in}"
        return cache_data.response
    return wrapper
