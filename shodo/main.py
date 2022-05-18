import os.path
import time
from pathlib import Path
from urllib.parse import urlparse

import click

from shodo.api import download_image, list_post_files


@click.group()
def cli():
    ...


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
