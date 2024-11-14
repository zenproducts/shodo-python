import asyncio
from typing import Optional

import aiohttp

from shodo.asyncio.api import lint_create, lint_result
from shodo.lint import Lint, LintFailed, LintResult, Message


async def lint(body: str, is_html: bool, profile: Optional[str] = None) -> LintResult:
    async with aiohttp.ClientSession() as session:
        create_res = await lint_create(body, is_html, profile, session)

        status = Lint.STATUS_PROCESSING
        pause = 0.5
        while status == Lint.STATUS_PROCESSING:
            await asyncio.sleep(pause)
            result_res = await lint_result(create_res.lint_id, profile, session)
            status = result_res.status

            messages = [Message.load(m) for m in result_res.messages]
            messages = sorted(messages, key=lambda m: (m.from_.line, m.from_.ch))
            pause *= 2

        if status == Lint.STATUS_FAILED:
            raise LintFailed

        return LintResult(status=status, messages=messages, updated=result_res.updated)
