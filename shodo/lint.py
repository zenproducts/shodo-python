import time
from dataclasses import asdict, dataclass
from datetime import datetime
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


class Lint:
    STATUS_PROCESSING = "processing"
    STATUS_FAILED = "failed"

    def __init__(self, body, lint_id, profile):
        self.body = body
        self.lint_id = lint_id
        self.body = None
        self.status = self.STATUS_PROCESSING
        self.messages = []
        self.profile = profile

    def results(self):
        while self.status == self.STATUS_PROCESSING:
            time.sleep(0.5)
            res = lint_result(self.lint_id, self.profile)
            self.status = res.status
            msgs = [Message.load(m) for m in res.messages]
            self.messages = sorted(msgs, key=lambda m: (m.from_.line, m.from_.ch))

        if self.status == self.STATUS_FAILED:
            raise LintFailed

        return self.messages

    def __repr__(self):
        return f"Lint({self.lint_id})"

    @classmethod
    def start(cls, body: str, is_html: bool = False, profile: Optional[str] = None):
        res = lint_create(body, is_html, profile)
        return cls(body, res.lint_id, profile)


def lint(body: str, is_html: bool = False, profile: Optional[str] = None) -> LintResult:
    create_res = lint_create(body, is_html, profile)

    status = Lint.STATUS_PROCESSING
    messages: List[Message] = []
    updated: datetime = datetime.now()
    pause = 0.5
    while status == Lint.STATUS_PROCESSING:
        time.sleep(pause)
        result_res = lint_result(create_res.lint_id, profile)
        status = result_res.status
        updated = result_res.updated

        msgs = [Message.load(m) for m in result_res.messages]
        messages = sorted(msgs, key=lambda m: (m.from_.line, m.from_.ch))
        pause *= 2

    if status == Lint.STATUS_FAILED:
        raise LintFailed

    return LintResult(status=status, messages=messages, updated=updated)
