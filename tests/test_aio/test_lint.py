from datetime import datetime, timezone
from aioresponses import aioresponses

import pytest
from shodo.aio.lint import lint


@pytest.mark.asyncio
async def test_lint(credential):
    with aioresponses() as m:
        m.post(
            "https://api.shodo.ink/@shodo/shodo/lint/",
            payload={
                "lint_id": "spam-spam-spam",
                "monthly_amount": 100,
                "current_usage": 10,
                "len_body": 10,
                "len_used": 10,
            },
        )
        m.get(
            "https://api.shodo.ink/@shodo/shodo/lint/spam-spam-spam/",
            payload={"status": "done", "updated": 1_700_000_000, "messages": []},
        )
        actual = await lint("body", is_html=False)

        assert actual.status == "done"
        assert actual.messages == []
        assert actual.updated.timetuple()[:6] == (2023, 11, 15, 7, 13, 20)
        m.assert_called_with(
            "https://api.shodo.ink/@shodo/shodo/lint/",
            "post",
            json={
                "body": "body",
                "type": "text",
            },
            headers={"Authorization": "Bearer test-token"},
        )
        m.assert_called_with(
            "https://api.shodo.ink/@shodo/shodo/lint/spam-spam-spam/",
            "get",
            headers={"Authorization": "Bearer test-token"},
        )
