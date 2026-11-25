from __future__ import annotations

import json
import os
import re
import shutil
import signal
import subprocess
import time
from pathlib import Path
from typing import Any

from scripts.evolution.backends.base import BackendError, BackendRequest, BackendResponse
from scripts.evolution.backends.schema import validate_json
from scripts.evolution.common import atomic_write_json, atomic_write_text


class CodexCliBackend:
    """Codex CLI adapter. It never loads a prior conversation or requests more privilege."""

    name = "codex-cli"
    REQUIRED_FLAGS = ("--ephemeral", "--json", "--output-schema", "--output-last-message", "--sandbox")

    def __init__(self, executable: str = "codex", model: str | None = None, reasoning_effort: str | None = None, search: bool = True):
        self.executable = shutil.which(executable) or executable
        self.model = model
        self.reasoning_effort = reasoning_effort
        self.search = search
        self.search_supported: bool | None = None

    def _load_search_capability(self) -> bool:
        if self.search_supported is None:
            try:
                result = subprocess.run([self.executable, "exec", "--help"], capture_output=True, text=True, timeout=10)
            except (OSError, subprocess.TimeoutExpired) as exc:
                raise BackendError("unsupported_cli", f"could not inspect Codex exec capabilities: {type(exc).__name__}", "healthcheck") from exc
            if result.returncode != 0:
                raise BackendError("unsupported_cli", "Codex CLI exec --help failed", "healthcheck")
            self.search_supported = "--search" in (result.stdout + result.stderr)
        return self.search_supported

    def healthcheck(self) -> dict[str, Any]:
        if not shutil.which(self.executable):
            raise BackendError("unavailable", "Codex CLI executable was not found", "healthcheck")
        version = subprocess.run([self.executable, "--version"], capture_output=True, text=True, timeout=10)
        help_result = subprocess.run([self.executable, "exec", "--help"], capture_output=True, text=True, timeout=10)
        help_text = help_result.stdout + help_result.stderr
        self.search_supported = "--search" in help_text
        missing = [flag for flag in self.REQUIRED_FLAGS if flag not in help_text]
        if version.returncode != 0 or help_result.returncode != 0 or missing:
            raise BackendError("unsupported_cli", f"Codex CLI is missing required exec support: {', '.join(missing) or 'version/help failed'}", "healthcheck")
        login = subprocess.run([self.executable, "login", "status"], capture_output=True, text=True, timeout=10)
        login_text = (login.stdout + login.stderr).strip()
        if login.returncode != 0 or "Logged in" not in login_text:
            raise BackendError("authentication", "Codex CLI has no usable login state", "healthcheck")
        # Keep only the non-secret status and version; never persist CLI auth output beyond this check.
        return {"version": version.stdout.strip(), "logged_in": True, "login_method": login_text.splitlines()[0] if login_text else "unavailable", "supported_flags": [flag for flag in self.REQUIRED_FLAGS if flag in help_text], "ephemeral": True, "search_flag_supported": self.search_supported}

    @staticmethod
    def _classify(text: str) -> tuple[str, bool]:
        lowered = text.lower()
        if any(term in lowered for term in ("invalid_json_schema", "invalid schema", "response_format", "text.format.schema")):
            return "schema", False
        if any(term in lowered for term in ("rate limit", "quota exceeded", "insufficient_quota", "usage limit")):
            return "quota", False
        if any(term in lowered for term in ("unauthorized", "not logged in", "authentication", "invalid token")):
            return "authentication", False
        if any(term in lowered for term in ("network", "connection reset", "timed out", "temporarily unavailable", "dns")):
            return "network", True
        return "process_exit", False

    @staticmethod
    def _read_events(path: Path) -> tuple[list[dict[str, Any]], dict[str, Any] | str, str | None]:
        events: list[dict[str, Any]] = []
        usage: dict[str, Any] | str = "unavailable"
        model: str | None = None
        if not path.exists():
            return events, usage, model
        for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
            try:
                event = json.loads(line)
            except json.JSONDecodeError:
                continue
            if not isinstance(event, dict):
                continue
            events.append(event)
            if isinstance(event.get("model"), str):
                model = event["model"]
            payload = event.get("payload", event)
            if isinstance(payload, dict):
                if isinstance(payload.get("model"), str):
                    model = payload["model"]
                candidate_usage = payload.get("usage")
                if isinstance(candidate_usage, dict) and any(k in candidate_usage for k in ("input_tokens", "output_tokens", "total_tokens")):
                    usage = {k: candidate_usage[k] for k in ("input_tokens", "output_tokens", "total_tokens") if k in candidate_usage}
        return events, usage, model

    @staticmethod
    def _scan_started_search_calls(path: Path, offset: int, pending: bytes) -> tuple[int, bytes, int]:
        if not path.exists():
            return offset, pending, 0
        with path.open("rb") as stream:
            stream.seek(offset)
            chunk = stream.read()
        offset += len(chunk)
        pieces = (pending + chunk).split(b"\n")
        pending = pieces.pop()
        started = 0
        for line in pieces:
            try:
                event = json.loads(line)
            except (json.JSONDecodeError, UnicodeDecodeError):
                continue
            if not isinstance(event, dict):
                continue
            item = event.get("item")
            if event.get("type") == "item.started" and isinstance(item, dict) and item.get("type") == "web_search":
                started += 1
        return offset, pending, started

    def invoke(self, request: BackendRequest) -> BackendResponse:
        if request.sandbox not in {"read-only", "workspace-write"}:
            raise BackendError("permission", f"sandbox mode is not allowed: {request.sandbox}", request.task_id)
        search_supported = self._load_search_capability()
        task_dir = request.task_dir
        task_dir.mkdir(parents=True, exist_ok=True, mode=0o700)
        os.chmod(task_dir, 0o700)
        schema_path = task_dir / "output-schema.json"
        event_path = task_dir / "events.jsonl"
        stderr_path = task_dir / "stderr.log"
        message_path = task_dir / "last-message.json"
        prompt_path = task_dir / "prompt.txt"
        atomic_write_json(schema_path, request.schema)
        atomic_write_text(prompt_path, request.prompt, mode=0o600)
        args = [
            self.executable, "exec", "--ephemeral", "--json", "--sandbox", request.sandbox,
            "--output-schema", str(schema_path), "--output-last-message", str(message_path),
            "--cd", str(request.workspace),
        ]
        if request.search and self.search and search_supported:
            args.append("--search")
        if request.model or self.model:
            args.extend(["--model", request.model or self.model or ""])
        effort = request.reasoning_effort or self.reasoning_effort
        if effort:
            args.extend(["-c", f'model_reasoning_effort="{effort}"'])
        args.append("-")
        started = time.monotonic()
        event_offset = 0
        event_pending = b""
        search_call_count = 0
        with event_path.open("wb") as stdout_stream, stderr_path.open("wb") as stderr_stream:
            os.chmod(event_path, 0o600)
            os.chmod(stderr_path, 0o600)
            try:
                process = subprocess.Popen(
                    args, cwd=request.workspace, stdin=subprocess.PIPE, stdout=stdout_stream, stderr=stderr_stream,
                    start_new_session=True,
                )
            except OSError as exc:
                raise BackendError("unavailable", f"could not start Codex CLI: {type(exc).__name__}: {exc}", request.task_id, metadata={"logs": str(task_dir)}) from exc
            try:
                if process.stdin is not None:
                    process.stdin.write(request.prompt.encode("utf-8"))
                    process.stdin.close()
                deadline = started + max(1, request.timeout_seconds)
                while process.poll() is None:
                    event_offset, event_pending, new_search_calls = self._scan_started_search_calls(event_path, event_offset, event_pending)
                    search_call_count += new_search_calls
                    if search_call_count > max(0, int(request.max_search_calls)):
                        os.killpg(process.pid, signal.SIGTERM)
                        try:
                            process.wait(timeout=3)
                        except subprocess.TimeoutExpired:
                            os.killpg(process.pid, signal.SIGKILL)
                            process.wait(timeout=3)
                        raise BackendError("tool_budget", f"Codex task exceeded its {request.max_search_calls}-call web-search tool budget", request.task_id, metadata={"logs": str(task_dir), "search_calls": search_call_count})
                    if request.stop_requested and request.stop_requested():
                        os.killpg(process.pid, signal.SIGTERM)
                        try:
                            process.wait(timeout=3)
                        except subprocess.TimeoutExpired:
                            os.killpg(process.pid, signal.SIGKILL)
                            process.wait(timeout=3)
                        raise BackendError("stopped", "stop was requested while model task was running", request.task_id, metadata={"logs": str(task_dir)})
                    if time.monotonic() >= deadline:
                        os.killpg(process.pid, signal.SIGTERM)
                        try:
                            process.wait(timeout=3)
                        except subprocess.TimeoutExpired:
                            os.killpg(process.pid, signal.SIGKILL)
                            process.wait(timeout=3)
                        raise BackendError("timeout", f"Codex task exceeded {request.timeout_seconds} seconds", request.task_id, retryable=True, metadata={"logs": str(task_dir)})
                    time.sleep(0.25)
            except BrokenPipeError:
                process.wait(timeout=3)
            except KeyboardInterrupt:
                try:
                    os.killpg(process.pid, signal.SIGTERM)
                except ProcessLookupError:
                    pass
                try:
                    process.wait(timeout=3)
                except subprocess.TimeoutExpired:
                    try:
                        os.killpg(process.pid, signal.SIGKILL)
                    except ProcessLookupError:
                        pass
                    process.wait(timeout=3)
                raise
            return_code = process.wait(timeout=3)
        raw_events, usage, event_model = self._read_events(event_path)
        observed_search_calls = sum(1 for event in raw_events if event.get("type") == "item.started" and isinstance(event.get("item"), dict) and event["item"].get("type") == "web_search")
        if observed_search_calls > max(0, int(request.max_search_calls)):
            raise BackendError("tool_budget", f"Codex task emitted {observed_search_calls} web-search calls after exit, over the limit {request.max_search_calls}", request.task_id, metadata={"logs": str(task_dir), "search_calls": observed_search_calls})
        if not message_path.is_file():
            event_diagnostic = "\n".join(json.dumps(event, ensure_ascii=False) for event in raw_events)
            diagnostic = (stderr_path.read_text(encoding="utf-8", errors="replace") + "\n" + event_diagnostic)[-8000:]
            kind, retryable = self._classify(diagnostic)
            raise BackendError(kind, f"Codex CLI exited {return_code} without a final response", request.task_id, retryable=retryable, metadata={"logs": str(task_dir), "exit_code": return_code})
        raw = message_path.read_text(encoding="utf-8", errors="replace")
        try:
            output = json.loads(raw)
        except json.JSONDecodeError as exc:
            raise BackendError("invalid_json", f"Codex final response was not JSON: {exc}", request.task_id, metadata={"logs": str(task_dir)}) from exc
        schema_errors = validate_json(output, request.schema)
        if schema_errors:
            raise BackendError("schema", "; ".join(schema_errors[:10]), request.task_id, metadata={"logs": str(task_dir), "schema_errors": schema_errors})
        if return_code != 0:
            diagnostic = stderr_path.read_text(encoding="utf-8", errors="replace")[-4000:]
            kind, retryable = self._classify(diagnostic)
            raise BackendError(kind, f"Codex CLI exited with code {return_code}", request.task_id, retryable=retryable, metadata={"logs": str(task_dir)})
        return BackendResponse(
            task_id=request.task_id, role=request.role, output=output, backend=self.name,
            model=event_model or request.model or self.model, usage=usage,
            metadata={"event_count": len(raw_events), "logs": str(task_dir), "elapsed_seconds": round(time.monotonic() - started, 2)},
        )
