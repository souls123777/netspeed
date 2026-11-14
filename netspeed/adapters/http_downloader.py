"""Driven adapter: downloads a URL with urllib from the standard library."""

import time
from collections.abc import Callable
from http.client import HTTPException, HTTPResponse
from urllib.parse import urlsplit
from urllib.request import Request, urlopen

from netspeed import constants
from netspeed.domain import Measurement
from netspeed.ports import DownloadError


class UrllibDownloader:
    """Implements the ``Downloader`` port.

    Every call opens a new connection, so DNS, TCP and TLS setup are part of the
    measured time. Only the response body counts as received data.
    """

    def __init__(
        self,
        timeout_seconds: float = constants.REQUEST_TIMEOUT_SECONDS,
        chunk_size_bytes: int = constants.READ_CHUNK_SIZE_BYTES,
        clock: Callable[[], float] = time.perf_counter,
    ) -> None:
        self._timeout_seconds = timeout_seconds
        self._chunk_size_bytes = chunk_size_bytes
        self._clock = clock

    def download(self, url: str) -> Measurement:
        try:
            _ensure_supported_scheme(url)
            request = Request(url, headers={constants.HEADER_USER_AGENT: constants.USER_AGENT})
            started = self._clock()
            with urlopen(request, timeout=self._timeout_seconds) as response:
                bytes_received = self._read_to_end(response)
                elapsed_seconds = self._clock() - started
                _ensure_complete(response, bytes_received)
        except (OSError, HTTPException, ValueError) as error:
            message = constants.DOWNLOAD_FAILED_TEMPLATE.format(url=url, reason=error)
            raise DownloadError(message) from error
        return Measurement(bytes_received, elapsed_seconds)

    def _read_to_end(self, response: HTTPResponse) -> int:
        total = 0
        while chunk := response.read(self._chunk_size_bytes):
            total += len(chunk)
        return total


def _ensure_supported_scheme(url: str) -> None:
    # urllib also opens file:// and ftp://; a speed test must only speak HTTP(S).
    scheme = urlsplit(url).scheme
    if scheme not in constants.ALLOWED_URL_SCHEMES:
        raise DownloadError(
            constants.UNSUPPORTED_SCHEME_TEMPLATE.format(
                scheme=scheme, allowed=constants.ALLOWED_URL_SCHEMES_TEXT
            )
        )


def _ensure_complete(response: HTTPResponse, bytes_received: int) -> None:
    # http.client does not raise when a body is cut short of Content-Length.
    expected = response.headers.get(constants.HEADER_CONTENT_LENGTH)
    if expected is not None and int(expected) != bytes_received:
        raise DownloadError(
            constants.INCOMPLETE_RESPONSE_TEMPLATE.format(
                expected=expected, received=bytes_received
            )
        )
