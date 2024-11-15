import json
from datetime import datetime, timezone

from shodo.lint import lint


class TestLint:
    def test_lint(self, credential, responses):
        responses.add(
            "POST",
            "https://api.shodo.ink/@shodo/shodo/lint/",
            json={
                "lint_id": "spam-spam-spam",
                "monthly_amount": 100,
                "current_usage": 10,
                "len_body": 10,
                "len_used": 10,
            },
        )
        responses.add(
            "GET",
            "https://api.shodo.ink/@shodo/shodo/lint/spam-spam-spam/",
            json={
                "status": "done",
                "messages": [],
                "updated": 1_700_000_000,
            },
        )

        actual = lint("これはテストです", is_html=False, profile=None, _initial_pause=0)

        assert actual.status == "done"
        assert actual.messages == []
        assert actual.updated.timetuple()[:6] == (2023, 11, 15, 7, 13, 20)

        assert len(responses.calls) == 2
        assert json.loads(responses.calls[0].request.body.decode("utf-8")) == {
            "body": "これはテストです",
            "type": "text",
        }
