import asyncio
from pathlib import Path

from shodo.lint import LintResult

md_path = Path(__file__).parent / "demo.md"


async def async_lint_demo() -> LintResult:
    from shodo.asyncio import lint

    return await lint(md_path.read_text())


def lint_demo() -> LintResult:
    from shodo import lint

    return lint(md_path.read_text())


if __name__ == "__main__":
    # async
    async_result = asyncio.run(async_lint_demo())
    # sync
    sync_result = lint_demo()
