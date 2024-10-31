import time
from dataclasses import asdict, dataclass
from typing import Dict, Optional

from shodo.api import lint_create, lint_result


@dataclass
class Pos:
    line: int
    ch: int

    def __str__(self):
        return f"{self.line+1}:{self.ch+1}"

    def astuple(self):
        return self.line, self.ch


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
    def load(cls, data):
        data["from_"] = Pos(**data.pop("from"))
        data["to"] = Pos(**data.pop("to"))
        return cls(**data)

    def asdict(self):
        data = asdict(self)
        del data["from_"]
        data["from"] = self.from_.astuple()
        data["to"] = self.to.astuple()
        return data


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
            self.status, messages = lint_result(self.lint_id, self.profile)
            msgs = [Message.load(m) for m in messages]
            self.messages = sorted(msgs, key=lambda m: (m.from_.line, m.from_.ch))

        if self.status == self.STATUS_FAILED:
            raise LintFailed

        return self.messages

    def __repr__(self):
        return f"Lint({self.lint_id})"

    @classmethod
    def start(cls, body: str, is_html: bool = False, profile: Optional[str] = None):
        lint_id = lint_create(body, is_html, profile)
        return cls(body, lint_id, profile)
