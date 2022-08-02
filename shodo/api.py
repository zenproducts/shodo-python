import time
from pathlib import Path

import requests

from shodo import conf


def api_path(path):
    return conf()["API_ROOT"].rstrip("/") + "/" + path.strip("/") + "/"


def shodo_auth(r):
    r.headers["Authorization"] = "Bearer " + conf()["API_TOKEN"]
    return r


def lint_create(body: str) -> str:
    res = requests.post(api_path("lint/"), json={"body": body}, auth=shodo_auth)
    res.raise_for_status()
    return res.json()["lint_id"]


def lint_result(lint_id: str) -> (str, list):
    res = requests.get(api_path(f"lint/{lint_id}/"), auth=shodo_auth)
    res.raise_for_status()
    data = res.json()
    return data["status"], data["messages"]


def download_image(image_url: str, image_path: Path):
    res = requests.get(image_url)
    res.raise_for_status()
    image_path.write_bytes(res.content)


def list_post_files(in_tree=False):
    page = 1
    params = {}
    if in_tree:
        params["in_tree"] = "1"

    while True:
        res = requests.get(
            api_path("files/"),
            auth=shodo_auth,
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
