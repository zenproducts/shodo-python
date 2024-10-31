import json
import os
from pathlib import Path
from typing import Optional

SHODO_TOKEN = "SHODO_API_TOKEN"
SHODO_ROOT = "SHODO_API_ROOT"
OLD_CREDENTIALS_PATH = "~/.shodo/credentials"


def get_path():
    config_path = Path(os.environ.get("XDG_CONFIG_HOME", "~/.config/"))
    config_path = config_path.expanduser()
    return config_path / "shodo/credentials"


def save_credentials(root: str, token: str, profile: str):
    c = get_path()
    if not c.parent.exists():
        c.parent.mkdir()

    if c.exists():
        d = json.loads(c.read_text(encoding="utf-8"))
    else:
        d = {}

    d[profile] = {
        SHODO_ROOT: root,
        SHODO_TOKEN: token,
    }
    c.write_text(json.dumps(d, indent=2), encoding="utf-8")


def load_credentials(profile: Optional[str] = None):
    p = get_path()
    if not p.exists():
        p = Path(OLD_CREDENTIALS_PATH).expanduser()
        if not p.exists():
            raise FileNotFoundError(
                "Use 'shodo login' to save credentials before running"
            )

    d = json.loads(p.read_text(encoding="utf-8"))
    return d[profile]


def conf(profile: Optional[str] = None):
    if not profile and SHODO_TOKEN in os.environ and SHODO_ROOT in os.environ:
        c = os.environ
    else:
        c = load_credentials(profile)
    return {
        "API_ROOT": c[SHODO_ROOT],
        "API_TOKEN": c[SHODO_TOKEN],
    }
