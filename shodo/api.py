import time
from pathlib import Path

import requests

from shodo import conf


def api_path(path):
    return conf()["API_ROOT"].rstrip("/") + "/" + path.strip("/") + "/"


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
            headers={
                "Authorization": "Bearer " + conf()["API_TOKEN"],
            },
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
