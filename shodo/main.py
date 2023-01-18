import os.path
import sys
import time
from getpass import getpass
from pathlib import Path
from urllib.parse import urlparse

import click

from shodo.api import download_image, list_post_files
from shodo.conf import save_credentials
from shodo.lint import Lint


@click.group()
def cli():
    ...


@cli.command()
def login():
    root = input("APIルート: ")
    token = getpass("APIトークン:")
    save_credentials(root, token)


@cli.command()
@click.argument("filename")
def lint(filename):
    body = Path(filename).read_text(encoding="utf-8")
    if not body:
        return

    linting = Lint.start(body)
    print("Linting...")
    for message in linting.results():
        color = "red" if message.severity == message.ERROR else "yellow"
        body_highlight = (
            body[message.index - 10 : message.index]
            + click.style(
                body[message.index : message.index_to]
                + (f"（→ {message.after or 'トル'}）" if message.after is not None else ""),
                color,
            )
            + body[message.index_to : message.index_to + 10]
        ).replace("\n", " ")
        print(message.from_, message.message)
        print("    ", body_highlight)

    if linting.messages:
        sys.exit(1)


@cli.command()
@click.option("--target", help="Target directory to save files", default="docs")
@click.option("--in-tree", help="Download only files with task Folder", default=False)
def download(target, in_tree):
    base_dir = Path() / target
    for file in list_post_files(in_tree=in_tree):
        dir_path = base_dir / (file["directory_path"] or "未分類")
        dir_path.mkdir(parents=True, exist_ok=True)

        body = file["body"]
        for i, image in enumerate(file["images"], start=1):
            url = image["url"]
            _, ext = os.path.splitext(urlparse(url).path)

            image_path = dir_path / "images" / f"{file['number']}_{i}{ext}"
            image_path.parent.mkdir(parents=True, exist_ok=True)

            download_image(url, image_path)
            body = body.replace(url, f"./images/{image_path.name}")
            click.echo(f"Downloaded Image {image_path}")
            time.sleep(0.05)

        file_path = dir_path / file["filename"]
        file_path.write_text(body)
        click.echo(f"Downloaded {file_path}")
