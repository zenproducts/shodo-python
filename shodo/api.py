import time
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Generator, List, Optional

import requests

from shodo.conf import conf

try:
    from zoneinfo import ZoneInfo
    JST = ZoneInfo("Asia/Tokyo")
except ImportError:
    from datetime import timedelta, timezone
    JST = timezone(timedelta(hours=+9), "JST")


def api_path(path, profile) -> str:
    return conf(profile).api_root.rstrip("/") + "/" + path.strip("/") + "/"


def shodo_auth(
    r: requests.PreparedRequest, profile: Optional[str] = None
) -> requests.PreparedRequest:
    r.headers["Authorization"] = "Bearer " + conf(profile).api_token
    return r


@dataclass(frozen=True)
class LintCreateResponse:
    lint_id: str
    monthly_amount: int
    current_usage: int
    len_body: int
    len_used: int


@dataclass
class LintResultResponse:
    status: str
    messages: List[Dict[str, Any]]
    updated: datetime

    def __post_init__(self) -> None:
        if isinstance(self.updated, int):
            self.updated = datetime.fromtimestamp(self.updated, JST)


def lint_create(
    body: str, is_html: bool = False, profile: Optional[str] = None
) -> LintCreateResponse:
    res = requests.post(
        api_path("lint/", profile),
        json={"body": body, "type": "html" if is_html else "text"},
        auth=lambda r: shodo_auth(r, profile),
    )
    res.raise_for_status()
    return LintCreateResponse(**res.json())


def lint_result(lint_id: str, profile: Optional[str] = None) -> LintResultResponse:
    res = requests.get(
        api_path(f"lint/{lint_id}/", profile), auth=lambda r: shodo_auth(r, profile)
    )
    res.raise_for_status()
    data = res.json()
    return LintResultResponse(**data)


def download_image(image_url: str, image_path: Path) -> None:
    res = requests.get(image_url)
    res.raise_for_status()
    image_path.write_bytes(res.content)


def list_post_files(
    in_tree=False, profile: Optional[str] = None
) -> Generator[Dict[str, Any], None, None]:
    page = 1
    params: Dict[str, Any] = {}
    if in_tree:
        params["in_tree"] = "1"

    while True:
        res = requests.get(
            api_path("files/", profile),
            auth=lambda r: shodo_auth(r, profile),
            params={
                "page": page,
                **params,
            },
        )
        res.raise_for_status()
        data = res.json()
        yield from data["results"]

        if data["next"] is None:
            break
        page += 1
        time.sleep(0.5)
