from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Protocol


@dataclass(frozen=True)
class BackendRequest:
    task_id: str
    role: str
    prompt: str
    schema: dict[str, Any]
    workspace: Path
    task_dir: Path
    timeout_seconds: int
    sandbox: str = "read-only"
    search: bool = True
    max_search_calls: int = 8
    model: str | None = None
    reasoning_effort: str | None = None
    stop_requested: Callable[[], bool] | None = field(default=None, compare=False, repr=False)


@dataclass
class BackendResponse:
    task_id: str
    role: str
    output: dict[str, Any]
    backend: str
    model: str | None = None
    usage: dict[str, Any] | str = "unavailable"
    metadata: dict[str, Any] = field(default_factory=dict)


class BackendError(RuntimeError):
    def __init__(self, kind: str, message: str, task_id: str, retryable: bool = False, metadata: dict[str, Any] | None = None):
        super().__init__(message)
        self.kind = kind
        self.task_id = task_id
        self.retryable = retryable
        self.metadata = metadata or {}


class Backend(Protocol):
    name: str

    def invoke(self, request: BackendRequest) -> BackendResponse: ...
