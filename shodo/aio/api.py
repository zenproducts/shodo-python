from typing import Optional

from shodo.api import LintCreateResponse, LintResultResponse
from shodo.conf import Credential, conf

try:
    import aiohttp
except ImportError:
    raise ImportError(
        "Using shodo.aio, but the 'aiohttp' package is not installed. "
        "Make sure to install the 'async' extra by running 'pip install shodo[async]'"
    )


def api_path(cred: Credential, path: str) -> str:
    return cred.api_root.rstrip("/") + "/" + path.strip("/") + "/"


async def lint_create(
    body: str,
    is_html: bool,
    profile: Optional[str] = None,
    session: Optional[aiohttp.ClientSession] = None,
) -> LintCreateResponse:
    async def post(s: aiohttp.ClientSession) -> LintCreateResponse:
        cred = conf(profile)
        headers = {
            "Authorization": "Bearer " + cred.api_token,
        }
        json_data = {
            "body": body,
            "type": "html" if is_html else "text",
        }
        async with s.post(api_path(cred, "lint/"), headers=headers, json=json_data) as res:
            res.raise_for_status()
            data = await res.json()
            return LintCreateResponse(**data)

    if session:
        return await post(session)
    else:
        async with aiohttp.ClientSession() as session:
            return await post(session)


async def lint_result(
    lint_id: str, profile: Optional[str] = None, session: Optional[aiohttp.ClientSession] = None
) -> LintResultResponse:
    async def get(s: aiohttp.ClientSession) -> LintResultResponse:
        cred = conf(profile)
        headers = {
            "Authorization": "Bearer " + cred.api_token,
        }
        async with s.get(api_path(cred, "lint/" + lint_id + "/"), headers=headers) as res:
            res.raise_for_status()
            data = await res.json()
            return LintResultResponse(**data)

    if session:
        return await get(session)
    else:
        async with aiohttp.ClientSession() as session:
            return await get(session)
