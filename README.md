# Shodo Python CLI

## Installation

```bash
$ pip3 install shodo
```

## Configuration

These environment variables are required

* `SHODO_API_ROOT` Root endpoint for API (like `https://api.shodo.ink/@my-organization/my-project/`).
* `SHODO_API_TOKEN` Token to access each projects (Access to Shodo and see projects' 「API連携」 settings page)

## Usage

Download all of Markdown posts and images!

```bash
$ shodo download --target=docs
```

Options:

```
Usage: shodo download [OPTIONS]

Options:
  --target TEXT      Target directory to save files
  --in-tree BOOLEAN  Download only files with task Folder
  --help             Show this message and exit.
```
