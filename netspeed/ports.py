"""Ports: the contracts the application core needs from the outside world."""

from typing import Protocol

from netspeed.domain import Measurement


class DownloadError(Exception):
    """A download could not be completed. The message is meant for the user."""


class Downloader(Protocol):
    """Fetches an address completely and reports what was measured."""

    def download(self, url: str) -> Measurement:
        """Read the whole response body of ``url``.

        Raises:
            DownloadError: on any failure (network, HTTP status, timeout,
                truncated body, unsupported address).
        """
        ...
