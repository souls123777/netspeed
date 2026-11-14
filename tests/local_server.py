"""A tiny local HTTP server, so the tests never touch the real network."""

import contextlib
import threading
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any

LOCALHOST = "127.0.0.1"
ANY_FREE_PORT = 0

ROUTE_PAYLOAD = "payload"  # /payload/<size>: a complete body of <size> bytes
ROUTE_TRUNCATED = "truncated"  # declares more bytes than it sends, then hangs up
ROUTE_SLOW = "slow"  # sends headers, then stalls until released

TRUNCATED_DECLARED_BYTES = 1_000
TRUNCATED_ACTUAL_BYTES = 100
SLOW_RELEASE_TIMEOUT_SECONDS = 10.0
FILLER_BYTE = b"x"


class LocalServer(ThreadingHTTPServer):
    daemon_threads = True

    def __init__(self) -> None:
        super().__init__((LOCALHOST, ANY_FREE_PORT), _Handler)
        self.user_agents: list[str] = []
        self.release_slow_responses = threading.Event()

    @property
    def base_url(self) -> str:
        return f"http://{LOCALHOST}:{self.server_port}"


class _Handler(BaseHTTPRequestHandler):
    server: LocalServer

    def do_GET(self) -> None:
        self.server.user_agents.append(self.headers.get("User-Agent", ""))
        route, _, argument = self.path.strip("/").partition("/")
        if route == ROUTE_PAYLOAD:
            size = int(argument)
            self._send_body(declared_bytes=size, actual_bytes=size)
        elif route == ROUTE_TRUNCATED:
            self._send_body(TRUNCATED_DECLARED_BYTES, TRUNCATED_ACTUAL_BYTES)
        elif route == ROUTE_SLOW:
            self._send_slow()
        else:
            self.send_error(HTTPStatus.NOT_FOUND)

    def _send_headers(self, content_length: int) -> None:
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-Length", str(content_length))
        self.end_headers()

    def _send_body(self, declared_bytes: int, actual_bytes: int) -> None:
        self._send_headers(declared_bytes)
        self.wfile.write(FILLER_BYTE * actual_bytes)

    def _send_slow(self) -> None:
        self._send_headers(len(FILLER_BYTE))
        self.server.release_slow_responses.wait(SLOW_RELEASE_TIMEOUT_SECONDS)
        with contextlib.suppress(OSError):  # the client has long gone
            self.wfile.write(FILLER_BYTE)

    def log_message(self, format: str, *args: Any) -> None:
        """Keep test output quiet."""
