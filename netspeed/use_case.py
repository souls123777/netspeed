"""Application layer: the benchmark scenario, independent of how data is fetched."""

from netspeed import constants
from netspeed.domain import BenchmarkReport, Measurement
from netspeed.ports import Downloader, DownloadError


def run_benchmark(
    downloader: Downloader,
    url: str,
    requests_count: int = constants.REQUESTS_COUNT,
) -> BenchmarkReport:
    """Download ``url`` ``requests_count`` times, strictly one after another.

    Sequential on purpose: concurrent requests would compete for the same
    bandwidth and the measurement would no longer describe a single download.
    Fails fast: the first failed request aborts the run.
    """
    measurements: list[Measurement] = []
    for number in range(1, requests_count + 1):
        try:
            measurements.append(downloader.download(url))
        except DownloadError as error:
            message = constants.REQUEST_FAILED_TEMPLATE.format(
                number=number, total=requests_count, reason=error
            )
            raise DownloadError(message) from error
    return BenchmarkReport(tuple(measurements))
