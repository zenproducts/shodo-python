import json
import os
from pathlib import Path

import pytest

from shodo.conf import UnableLocateCredentialsError, conf, load_credentials, save_credentials


@pytest.fixture
def credentials_path(tmp_path) -> Path:
    os.environ["XDG_CONFIG_HOME"] = str(tmp_path)
    yield tmp_path / "shodo" / "credentials"
    del os.environ["XDG_CONFIG_HOME"]


@pytest.fixture
def api_root() -> str:
    return "https://api.shodo.ink/@my-organization/"


@pytest.mark.parametrize("profile", ["default", "tests"], ids=["default", "tests"])
def test_save_credentials(credentials_path, api_root, profile):
    save_credentials(f"{api_root}{profile}/", "stub-token", profile)

    creds = json.loads(credentials_path.read_text())
    actual = creds[profile]

    assert actual == {
        "SHODO_API_ROOT": f"{api_root}{profile}/",
        "SHODO_API_TOKEN": "stub-token",
    }


class TestLoadCredentials:
    @pytest.mark.parametrize(
        "profile",
        [None, "default", "tests"],
        ids=["None", "default", "tests"],
    )
    def test_no_exist_credentials_file(self, credentials_path, profile):
        with pytest.raises(UnableLocateCredentialsError) as e:
            load_credentials(profile)

        assert e.value.msg == "Use 'shodo login' to save credentials before running."

    def test_exist_credentials_without_profile(self, credentials_path, api_root):
        save_credentials(f"{api_root}default/", "stub-token", "default")

        actual = load_credentials(None)

        assert actual == {
            "SHODO_API_ROOT": f"{api_root}default/",
            "SHODO_API_TOKEN": "stub-token",
        }

    @pytest.mark.parametrize("profile", ["default", "tests"], ids=["default", "tests"])
    def test_exist_credentials_with_profile(self, credentials_path, api_root, profile):
        save_credentials(f"{api_root}{profile}/", "stub-token", profile)

        actual = load_credentials(profile)

        assert actual == {
            "SHODO_API_ROOT": f"{api_root}{profile}/",
            "SHODO_API_TOKEN": "stub-token",
        }

    @pytest.mark.parametrize(
        "profile, expected",
        [
            (None, "Use 'shodo login' to save credentials before running."),
            ("default", "The config profile (default) could not be found."),
            ("tests", "The config profile (tests) could not be found."),
        ],
        ids=["None", "default", "tests"],
    )
    def test_not_found_profile(self, credentials_path, api_root, profile, expected):
        save_credentials(f"{api_root}{profile}/", "stub-token", "dummy")

        with pytest.raises(UnableLocateCredentialsError) as e:
            load_credentials(profile)

        assert e.value.msg == expected


class TestConf:
    @pytest.fixture
    def shodo_envs(self, api_root):
        os.environ["SHODO_API_ROOT"] = f"{api_root}default/"
        os.environ["SHODO_API_TOKEN"] = "stub-token"
        yield
        del os.environ["SHODO_API_ROOT"]
        del os.environ["SHODO_API_TOKEN"]

    def test_profile_and_envs_is_none(self, credentials_path):
        with pytest.raises(UnableLocateCredentialsError) as e:
            conf(None)

        assert e.value.msg == "Use 'shodo login' to save credentials before running."

    def test_profile_is_none(self, credentials_path, shodo_envs, api_root):
        actual = conf(None)

        assert actual == {
            "API_ROOT": f"{api_root}default/",
            "API_TOKEN": "stub-token",
        }

    @pytest.mark.parametrize("profile", ["default", "tests"], ids=["default", "tests"])
    def test_envs_is_none(self, credentials_path, api_root, profile):
        save_credentials(f"{api_root}{profile}/", "stub-token", profile)

        actual = conf(profile)

        assert actual == {
            "API_ROOT": f"{api_root}{profile}/",
            "API_TOKEN": "stub-token",
        }

    def test_profile_and_envs_is_not_none(self, credentials_path, shodo_envs, api_root):
        save_credentials(f"{api_root}default/", "stub-token", "default")

        actual = conf("default")

        assert actual == {
            "API_ROOT": f"{api_root}default/",
            "API_TOKEN": "stub-token",
        }
