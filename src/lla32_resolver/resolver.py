"""Execution boundary for the archived 32-bit resolver payload."""

from __future__ import annotations

from dataclasses import dataclass
import os
from pathlib import Path
import subprocess
import tempfile

from .payload import DWORD_MASK, LLA32_PAYLOAD


class LLA32ResolverError(RuntimeError):
    """Base error for resolver failures."""


class UnsupportedPlatformError(LLA32ResolverError):
    """Raised when the resolver is invoked on a non-Windows host."""


class PayloadExecutionError(LLA32ResolverError):
    """Raised when the payload cannot be executed or cleaned up."""


@dataclass
class LLA32Resolver:
    """Compatibility facade around explicit LoadLibraryA resolution."""

    address: int | None = None

    def resolve(self) -> int:
        self.address = resolve_load_library_a()
        return self.address

    def get_address(self) -> int:
        return self.resolve()


def resolve_load_library_a() -> int:
    _require_windows()
    payload_path = _write_payload_executable()

    try:
        return _run_payload(payload_path)
    finally:
        _remove_payload(payload_path)


def _write_payload_executable() -> Path:
    with tempfile.NamedTemporaryFile(
        prefix="lla32_resolver_",
        suffix=".exe",
        delete=False,
    ) as payload_file:
        payload_file.write(LLA32_PAYLOAD)
        return Path(payload_file.name)


def _run_payload(payload_path: Path) -> int:
    try:
        completed = subprocess.run(
            [str(payload_path)],
            stdin=subprocess.DEVNULL,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=False,
        )
    except OSError as exc:
        raise PayloadExecutionError(f"Could not execute payload: {payload_path}") from exc

    return _normalize_exit_code(completed.returncode)


def _remove_payload(payload_path: Path) -> None:
    try:
        payload_path.unlink()
    except FileNotFoundError:
        return
    except OSError as exc:
        raise PayloadExecutionError(
            f"Payload ran, but temporary file could not be removed: {payload_path}"
        ) from exc


def _require_windows() -> None:
    if os.name != "nt":
        raise UnsupportedPlatformError("LLA32 payload execution requires Windows.")


def _normalize_exit_code(return_code: int) -> int:
    return return_code & DWORD_MASK
