import time
from dataclasses import asdict, dataclass
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from shodo.api import lint_create, lint_result


@dataclass
class Pos:
    line: int
    ch: int

    def __str__(self):
        return f"{self.line+1}:{self.ch+1}"

    def asdict(self):
        return {
            "line": self.line,
            "ch": self.ch,
        }


@dataclass
class Message:
    ERROR = "error"
    WARNING = "warning"

    code: str
    message: str
    severity: str
    from_: Pos
    to: Pos
    index: int
    index_to: int
    score: float
    before: Optional[str] = None
    after: Optional[str] = None
    operation: Optional[str] = None
    meta: Optional[Dict] = None

    @classmethod
    def load(cls, data: Dict[str, Any]):
        data["from_"] = Pos(**data.pop("from"))
        data["to"] = Pos(**data.pop("to"))
        return cls(**data)

    def asdict(self):
        data = asdict(self)
        del data["from_"]
        data["from"] = self.from_.asdict()
        data["to"] = self.to.asdict()
        return data


@dataclass(frozen=True)
class LintResult:
    status: str
    messages: List[Message]
    updated: datetime


class LintFailed(Exception):
    pass


class LintStatus(Enum):
    PROCESSING = "processing"
    FAILED = "failed"
    DONE = "done"


def lint(body: str, is_html: bool = False, profile: Optional[str] = None, _initial_pause: float=0.25) -> LintResult:
    create_res = lint_create(body, is_html, profile)

    status = LintStatus.PROCESSING.value
    pause = _initial_pause
    while status == LintStatus.PROCESSING.value:
        time.sleep(pause)
        result_res = lint_result(create_res.lint_id, profile)
        status = result_res.status

        msgs = [Message.load(m) for m in result_res.messages]
        messages = sorted(msgs, key=lambda m: (m.from_.line, m.from_.ch))
        if pause < 16:
            pause *= 2

    if status == LintStatus.FAILED.value:
        raise LintFailed

    return LintResult(status=status, messages=messages, updated=result_res.updated)
