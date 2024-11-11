import uuid
from pathlib import Path

import pytest
from click.testing import CliRunner

from shodo.conf import UnableLocateCredentialsError
from shodo.lint import Lint, Message
from shodo.main import cli


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture
def filename() -> Path:
    return Path(__file__).parent.parent / "demo" / "demo.md"


class TestLogin:
    def test_no_profile(self, mocker, runner):
        mocker.patch(
            "builtins.input",
            return_value="https://api.shodo.ink/@my-organization/my-project/",
        )
        mocker.patch("shodo.main.getpass", return_value="stub-token")
        m_save_credentials = mocker.patch("shodo.main.save_credentials")

        actual = runner.invoke(cli, ["login"])

        assert actual.exit_code == 0
        assert m_save_credentials.call_count == 1
        assert m_save_credentials.call_args == (
            (
                "https://api.shodo.ink/@my-organization/my-project/",
                "stub-token",
                "default",
            ),
        )

    @pytest.mark.parametrize("profile", ["default", "tests"], ids=["default", "tests"])
    def test_with_profile(self, mocker, runner, profile):
        mocker.patch(
            "builtins.input",
            return_value=f"https://api.shodo.ink/@my-organization/{profile}/",
        )
        mocker.patch("shodo.main.getpass", return_value="stub-token")
        m_save_credentials = mocker.patch("shodo.main.save_credentials")

        actual = runner.invoke(cli, ["login", "--profile", profile])

        assert actual.exit_code == 0
        assert m_save_credentials.call_count == 1
        assert m_save_credentials.call_args == (
            (
                f"https://api.shodo.ink/@my-organization/{profile}/",
                "stub-token",
                profile,
            ),
        )


class TestLint:
    def test_no_profile(self, mocker, runner, filename):
        body = filename.read_text(encoding="utf-8")
        linting = Lint(body, str(uuid.uuid4()), None)
        m_lint = mocker.patch("shodo.main.Lint.start", return_value=linting)
        stub_results = [
            Message.load(data)
            for data in [
                {
                    "code": "variants:fuzzy",
                    "message": "表記ゆれがあります",
                    "severity": "error",
                    "to": {
                        "line": 0,
                        "ch": 12,
                    },
                    "index": 2,
                    "index_to": 12,
                    "score": 0.8888888888888888,
                    "before": "Shodo AI校正",
                    "after": "Shodo AI校正",
                    "operation": "replace",
                    "meta": {
                        "description": "",
                    },
                    "from": {
                        "line": 0,
                        "ch": 2,
                    },
                },
            ]
        ]
        mocker.patch.object(Lint, "results", return_value=stub_results)

        actual = runner.invoke(cli, args=["lint", str(filename)], color=True)

        assert actual.exit_code == 0
        assert (
            actual.output
            == "Linting...\n1:3 表記ゆれがあります\n     \x1b[31mShodo AI校正（→ Shodo AI校正）\x1b[0m  飛行機の欠便があ\n"
        )
        assert m_lint.call_count == 1
        assert m_lint.call_args == ((body,), {"is_html": False, "profile": None})

    @pytest.mark.parametrize("profile", ["default", "tests"], ids=["default", "tests"])
    def test_with_profile(self, mocker, runner, filename, profile):
        body = filename.read_text(encoding="utf-8")
        linting = Lint(body, str(uuid.uuid4()), profile)
        m_lint = mocker.patch("shodo.main.Lint.start", return_value=linting)
        mocker.patch.object(Lint, "results", return_value=[])

        actual = runner.invoke(cli, ["lint", str(filename), "--profile", profile])

        assert actual.exit_code == 0
        assert actual.output == "Linting...\n"
        assert m_lint.call_count == 1
        assert m_lint.call_args == ((body,), {"is_html": False, "profile": profile})

    def test_no_existing_default_profile(self, mocker, filename, runner):
        body = filename.read_text(encoding="utf-8")
        m_lint = mocker.patch(
            "shodo.main.Lint.start",
            side_effect=UnableLocateCredentialsError(
                "Use 'shodo login' to save credentials before running."
            ),
        )

        actual = runner.invoke(cli, ["lint", str(filename)])

        assert actual.exit_code == 1
        assert actual.exception.msg == "Use 'shodo login' to save credentials before running."
        assert m_lint.call_count == 1
        assert m_lint.call_args == ((body,), {"is_html": False, "profile": None})

    def test_not_found_profile(self, mocker, filename, runner):
        body = filename.read_text(encoding="utf-8")
        m_lint = mocker.patch(
            "shodo.main.Lint.start",
            side_effect=UnableLocateCredentialsError(
                "The config profile (tests) could not be found."
            ),
        )

        actual = runner.invoke(cli, ["lint", str(filename), "--profile", "tests"])

        assert actual.exit_code == 1
        assert actual.exception.msg == "The config profile (tests) could not be found."
        assert m_lint.call_count == 1
        assert m_lint.call_args == ((body,), {"is_html": False, "profile": "tests"})


class TestDownload:
    def test_no_profile(self, tmp_path, mocker, filename, runner):
        stub_files = [
            {
                "number": 1,
                "directory_path": None,
                "filename": "Shodo_AI校正.md",
                "body": filename.read_text(encoding="utf-8"),
                "version": 3,
                "committed_at": "2024-11-05T15:05:10.838949+09:00",
                "images": [],
                "task": {},  # not used
            }
        ]
        m_lint_post_files = mocker.patch("shodo.main.list_post_files", return_value=stub_files)

        actual = runner.invoke(cli, ["download", "--target", str(tmp_path)])

        assert actual.exit_code == 0
        assert actual.output == f"Downloaded {tmp_path}/未分類/Shodo_AI校正.md\n"
        assert m_lint_post_files.call_count == 1
        assert m_lint_post_files.call_args == ((), {"in_tree": False, "profile": None})
        directory_path = tmp_path / "未分類"
        assert directory_path.exists()
        md_path = directory_path / "Shodo_AI校正.md"
        assert md_path.exists()

    @pytest.mark.parametrize("profile", ["default", "tests"], ids=["default", "tests"])
    def test_with_profile(self, tmp_path, mocker, runner, profile):
        m_lint_post_files = mocker.patch("shodo.main.list_post_files", return_value=[])

        actual = runner.invoke(cli, ["download", "--target", str(tmp_path), "--profile", profile])

        assert actual.exit_code == 0
        assert actual.output == ""
        assert m_lint_post_files.call_count == 1
        assert m_lint_post_files.call_args == ((), {"in_tree": False, "profile": profile})

    def test_no_existing_default_profile(self, tmp_path, mocker, runner):
        m_lint_post_files = mocker.patch(
            "shodo.main.list_post_files",
            side_effect=UnableLocateCredentialsError(
                "Use 'shodo login' to save credentials before running."
            ),
        )

        actual = runner.invoke(cli, ["download", "--target", str(tmp_path)])

        assert actual.exit_code == 1
        assert actual.exception.msg == "Use 'shodo login' to save credentials before running."
        assert m_lint_post_files.call_count == 1
        assert m_lint_post_files.call_args == ((), {"in_tree": False, "profile": None})

    def test_not_found_profile(self, tmp_path, mocker, runner):
        m_lint_post_files = mocker.patch(
            "shodo.main.list_post_files",
            side_effect=UnableLocateCredentialsError(
                "The config profile (tests) could not be found."
            ),
        )

        actual = runner.invoke(cli, ["download", "--target", str(tmp_path), "--profile", "tests"])

        assert actual.exit_code == 1
        assert actual.exception.msg == "The config profile (tests) could not be found."
        assert m_lint_post_files.call_count == 1
        assert m_lint_post_files.call_args == ((), {"in_tree": False, "profile": "tests"})
