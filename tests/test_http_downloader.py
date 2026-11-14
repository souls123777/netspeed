import socket

import pytest

from netspeed import constants
from netspeed.adapters.http_downloader import UrllibDownloader
from netspeed.ports import DownloadError
from tests.local_server import LOCALHOST, LocalServer

PAYLOAD_SIZE = 10_123  # not a multiple of the chunk size below, on purpose
SMALL_CHUNK_SIZE = 1_000
SHORT_TIMEOUT_SECONDS = 0.2


def test_counts_every_body_byte_across_several_chunks(local_server: LocalServer) -> None:
    downloader = UrllibDownloader(chunk_size_bytes=SMALL_CHUNK_SIZE)

    measurement = downloader.download(f"{local_server.base_url}/payload/{PAYLOAD_SIZE}")

    assert measurement.bytes_received == PAYLOAD_SIZE
    assert measurement.elapsed_seconds > 0


def test_elapsed_time_comes_from_the_injected_clock(local_server: LocalServer) -> None:
    clock = iter([10.0, 12.5]).__next__
    downloader = UrllibDownloader(clock=clock)

    measurement = downloader.download(f"{local_server.base_url}/payload/{PAYLOAD_SIZE}")

    assert measurement.elapsed_seconds == pytest.approx(2.5)


def test_sends_its_own_user_agent(local_server: LocalServer) -> None:
    UrllibDownloader().download(f"{local_server.base_url}/payload/1")

    assert local_server.user_agents == [constants.USER_AGENT]


def test_http_error_status_becomes_download_error(local_server: LocalServer) -> None:
    with pytest.raises(DownloadError, match="404"):
        UrllibDownloader().download(f"{local_server.base_url}/missing")


def test_body_shorter_than_content_length_is_an_error(local_server: LocalServer) -> None:
    with pytest.raises(DownloadError, match="incomplete response"):
        UrllibDownloader().download(f"{local_server.base_url}/truncated")


def test_stalled_response_times_out(local_server: LocalServer) -> None:
    downloader = UrllibDownloader(timeout_seconds=SHORT_TIMEOUT_SECONDS)

    with pytest.raises(DownloadError, match="timed out"):
        downloader.download(f"{local_server.base_url}/slow")


def test_refused_connection_becomes_download_error() -> None:
    with socket.socket() as sock:
        sock.bind((LOCALHOST, 0))
        closed_port = sock.getsockname()[1]

    with pytest.raises(DownloadError):
        UrllibDownloader().download(f"http://{LOCALHOST}:{closed_port}/")


@pytest.mark.parametrize(
    "url",
    ["file:///etc/passwd", "ftp://example.test/file", "example.test/file", ""],
)
def test_rejects_anything_but_http_and_https(url: str) -> None:
    with pytest.raises(DownloadError, match="unsupported URL scheme"):
        UrllibDownloader().download(url)
