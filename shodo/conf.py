import json
import os
from pathlib import Path

SHODO_TOKEN = "SHODO_API_TOKEN"
SHODO_ROOT = "SHODO_API_ROOT"
CREDENTIALS_PATH = "~/.shodo/credentials"


def get_path():
    return Path(CREDENTIALS_PATH).expanduser()


def ensure_credentials():
    c = get_path()
    if not c.parent.exists():
        c.parent.mkdir()
    if not c.exists():
        c.write_text("{}", encoding="utf-8")


def save_credentials(root: str, token: str):
    ensure_credentials()
    c = get_path()
    d = json.loads(c.read_text(encoding="utf-8"))
    d["default"] = {
        SHODO_ROOT: root,
        SHODO_TOKEN: token,
    }
    c.write_text(json.dumps(d, indent=2), encoding="utf-8")


def load_credentials():
    d = json.loads(get_path().read_text(encoding="utf-8"))
    return d["default"]


def conf():
    if SHODO_TOKEN in os.environ and SHODO_ROOT in os.environ:
        c = os.environ
    else:
        c = load_credentials()
    return {
        "API_ROOT": c[SHODO_ROOT],
        "API_TOKEN": c[SHODO_TOKEN],
    }
