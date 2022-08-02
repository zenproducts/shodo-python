import time
from dataclasses import dataclass
from typing import Optional

from .api import lint_create, lint_result


@dataclass
class Pos:
    line: int
    ch: int

    def __str__(self):
        return f"{self.line+1}:{self.ch+1}"


@dataclass
class Message:
    ERROR = "error"
    WARNING = "warning"

    message: str
    severity: str
    from_: Pos
    to: Pos
    index: int
    index_to: int
    before: Optional[str] = None
    after: Optional[str] = None

    @classmethod
    def load(cls, data):
        data["from_"] = Pos(**data.pop("from"))
        data["to"] = Pos(**data.pop("to"))
        return cls(**data)


class LintFailed(Exception):
    pass


class Lint:
    STATUS_PROCESSING = "processing"
    STATUS_FAILED = "failed"

    def __init__(self, body, lint_id):
        self.body = body
        self.lint_id = lint_id
        self.body = None
        self.status = self.STATUS_PROCESSING
        self.messages = []

    def results(self):
        while self.status == self.STATUS_PROCESSING:
            time.sleep(.5)
            self.status, messages = lint_result(self.lint_id)
            self.messages = [Message.load(m) for m in messages]

        if self.status == self.STATUS_FAILED:
            raise LintFailed

        return self.messages

    def __repr__(self):
        return f"Lint({self.lint_id})"

    @classmethod
    def start(cls, body):
        lint_id = lint_create(body)
        return cls(body, lint_id)
