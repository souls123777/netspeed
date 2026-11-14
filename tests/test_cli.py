import pytest

from netspeed.adapters.cli import format_report, run
from netspeed.domain import BenchmarkReport, Measurement
from netspeed.ports import DownloadError

URL = "http://example.test/image.jpg"
REPORT = BenchmarkReport(
    (
        Measurement(bytes_received=1_000_000, elapsed_seconds=0.5),
        Measurement(bytes_received=1_500_000, elapsed_seconds=0.5),
    )
)
EXPECTED_OUTPUT = (
    "URL:                  http://example.test/image.jpg\n"
    "Requests:             2\n"
    "Total downloaded:     2.50 MB (2500000 bytes)\n"
    "Total time:           1.000 s\n"
    "Average request time: 0.500 s\n"
    "Download speed:       20.00 Mbit/s"
)


class StubDownloader:
    def __init__(self, error: BaseException | None = None) -> None:
        self._error = error

    def download(self, url: str) -> Measurement:
        if self._error is not None:
            raise self._error
        return Measurement(bytes_received=1_000_000, elapsed_seconds=0.5)


def test_format_report_is_stable() -> None:
    assert format_report(URL, REPORT) == EXPECTED_OUTPUT


def test_success_prints_report_to_stdout(capsys: pytest.CaptureFixture[str]) -> None:
    exit_code = run([URL], StubDownloader())

    captured = capsys.readouterr()
    assert exit_code == 0
    assert "Download speed:       16.00 Mbit/s" in captured.out
    assert captured.err == ""


def test_download_error_goes_to_stderr_with_exit_code_1(
    capsys: pytest.CaptureFixture[str],
) -> None:
    exit_code = run([URL], StubDownloader(DownloadError("boom")))

    captured = capsys.readouterr()
    assert exit_code == 1
    assert captured.out == ""
    assert captured.err.startswith("error: request 1 of 10 failed: boom")


def test_ctrl_c_exits_with_130(capsys: pytest.CaptureFixture[str]) -> None:
    exit_code = run([URL], StubDownloader(KeyboardInterrupt()))

    assert exit_code == 130
    assert capsys.readouterr().out == ""


def test_missing_url_is_a_usage_error() -> None:
    with pytest.raises(SystemExit) as exit_info:
        run([], StubDownloader())

    assert exit_info.value.code == 2
