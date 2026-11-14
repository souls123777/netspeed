"""Runs the real entry point as a subprocess against the local test server."""

import subprocess
import sys
from pathlib import Path

from tests.local_server import LocalServer

PROJECT_ROOT = Path(__file__).resolve().parent.parent
PAYLOAD_SIZE = 50_000
SUBPROCESS_TIMEOUT_SECONDS = 60


def _run_cli(url: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "-m", "netspeed", url],
        capture_output=True,
        text=True,
        cwd=PROJECT_ROOT,
        timeout=SUBPROCESS_TIMEOUT_SECONDS,
        check=False,
    )


def test_prints_report_after_exactly_ten_requests(local_server: LocalServer) -> None:
    result = _run_cli(f"{local_server.base_url}/payload/{PAYLOAD_SIZE}")

    assert result.returncode == 0, result.stderr
    assert "Requests:             10" in result.stdout
    assert f"({PAYLOAD_SIZE * 10} bytes)" in result.stdout
    assert "Mbit/s" in result.stdout
    assert len(local_server.user_agents) == 10


def test_reports_failure_with_exit_code_1(local_server: LocalServer) -> None:
    result = _run_cli(f"{local_server.base_url}/missing")

    assert result.returncode == 1
    assert result.stdout == ""
    assert "request 1 of 10 failed" in result.stderr
    assert len(local_server.user_agents) == 1
