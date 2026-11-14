from collections.abc import Iterable

import pytest

from netspeed.domain import Measurement
from netspeed.ports import DownloadError
from netspeed.use_case import run_benchmark

URL = "http://example.test/image.jpg"
MEASUREMENT = Measurement(bytes_received=1_000, elapsed_seconds=0.5)


class FakeDownloader:
    """Replays scripted outcomes and records every requested URL."""

    def __init__(self, outcomes: Iterable[Measurement | Exception]) -> None:
        self._outcomes = iter(outcomes)
        self.requested_urls: list[str] = []

    def download(self, url: str) -> Measurement:
        self.requested_urls.append(url)
        outcome = next(self._outcomes)
        if isinstance(outcome, Exception):
            raise outcome
        return outcome


def test_makes_ten_requests_to_the_given_url_by_default() -> None:
    downloader = FakeDownloader([MEASUREMENT] * 10)

    report = run_benchmark(downloader, URL)

    assert downloader.requested_urls == [URL] * 10
    assert report.requests_count == 10


def test_request_count_can_be_overridden() -> None:
    downloader = FakeDownloader([MEASUREMENT] * 3)

    report = run_benchmark(downloader, URL, requests_count=3)

    assert len(downloader.requested_urls) == 3
    assert report.requests_count == 3


def test_keeps_measurements_in_request_order() -> None:
    outcomes = [Measurement(bytes_received=size, elapsed_seconds=1.0) for size in (10, 20, 30)]

    report = run_benchmark(FakeDownloader(outcomes), URL, requests_count=3)

    assert report.measurements == tuple(outcomes)


def test_fails_fast_and_names_the_failed_request() -> None:
    outcomes: list[Measurement | Exception] = [MEASUREMENT, MEASUREMENT, DownloadError("boom")]
    downloader = FakeDownloader(outcomes + [MEASUREMENT] * 7)

    with pytest.raises(DownloadError, match="request 3 of 10 failed: boom"):
        run_benchmark(downloader, URL)

    assert len(downloader.requested_urls) == 3
