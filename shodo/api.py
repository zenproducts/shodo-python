import time
from pathlib import Path
from typing import Optional

import requests

from shodo import conf


def api_path(path, profile):
    return conf(profile)["API_ROOT"].rstrip("/") + "/" + path.strip("/") + "/"


def shodo_auth(r, profile: Optional[str] = None):
    r.headers["Authorization"] = "Bearer " + conf(profile)["API_TOKEN"]
    return r


def lint_create(body: str, is_html: bool = False, profile: Optional[str] = None) -> str:
    res = requests.post(
        api_path("lint/", profile),
        json={"body": body, "type": "html" if is_html else "text"},
        auth=lambda r: shodo_auth(r, profile),
    )
    res.raise_for_status()
    return res.json()["lint_id"]


def lint_result(lint_id: str, profile: Optional[str] = None) -> (str, list):
    res = requests.get(
        api_path(f"lint/{lint_id}/", profile), auth=lambda r: shodo_auth(r, profile)
    )
    res.raise_for_status()
    data = res.json()
    return data["status"], data["messages"]


def download_image(image_url: str, image_path: Path):
    res = requests.get(image_url)
    res.raise_for_status()
    image_path.write_bytes(res.content)


def list_post_files(in_tree=False, profile: Optional[str] = None):
    page = 1
    params = {}
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
