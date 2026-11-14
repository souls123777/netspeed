import threading
from collections.abc import Iterator

import pytest

from tests.local_server import LOCALHOST, LocalServer


@pytest.fixture(autouse=True)
def bypass_proxies_for_localhost(monkeypatch: pytest.MonkeyPatch) -> None:
    """Corporate proxy variables must not hijack requests to the local test server."""
    for name in ("no_proxy", "NO_PROXY"):
        monkeypatch.setenv(name, LOCALHOST)


@pytest.fixture
def local_server() -> Iterator[LocalServer]:
    server = LocalServer()
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        yield server
    finally:
        server.release_slow_responses.set()
        server.shutdown()
        server.server_close()
        thread.join()
