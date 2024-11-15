import asyncio
from typing import Optional

import aiohttp

from shodo.aio.api import lint_create, lint_result
from shodo.lint import LintFailed, LintResult, LintStatus, Message


async def lint(body: str, is_html: bool = False, profile: Optional[str] = None, _initial_pause: float = 0.25) -> LintResult:
    async with aiohttp.ClientSession() as session:
        create_res = await lint_create(body, is_html, profile, session)

        status = LintStatus.PROCESSING.value
        pause = _initial_pause
        while status == LintStatus.PROCESSING.value:
            await asyncio.sleep(pause)
            result_res = await lint_result(create_res.lint_id, profile, session)
            status = result_res.status

            messages = [Message.load(m) for m in result_res.messages]
            messages = sorted(messages, key=lambda m: (m.from_.line, m.from_.ch))
            if pause < 16:
                pause *= 2

        if status == LintStatus.FAILED.value:
            raise LintFailed

        return LintResult(status=status, messages=messages, updated=result_res.updated)
