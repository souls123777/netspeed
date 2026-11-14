import pytest

from netspeed.domain import BenchmarkReport, Measurement


def test_measurement_rejects_negative_size() -> None:
    with pytest.raises(ValueError):
        Measurement(bytes_received=-1, elapsed_seconds=1.0)


@pytest.mark.parametrize("elapsed", [0.0, -0.5])
def test_measurement_rejects_non_positive_time(elapsed: float) -> None:
    with pytest.raises(ValueError):
        Measurement(bytes_received=1, elapsed_seconds=elapsed)


def test_report_rejects_empty_run() -> None:
    with pytest.raises(ValueError):
        BenchmarkReport(measurements=())


def test_report_totals_and_average() -> None:
    report = BenchmarkReport(
        (
            Measurement(bytes_received=1_000_000, elapsed_seconds=1.0),
            Measurement(bytes_received=3_000_000, elapsed_seconds=3.0),
        )
    )

    assert report.requests_count == 2
    assert report.total_bytes == 4_000_000
    assert report.total_seconds == pytest.approx(4.0)
    assert report.average_request_seconds == pytest.approx(2.0)


def test_speed_is_megabits_per_second() -> None:
    # 2 MB in 1 s is 16 Mbit/s (decimal megabits: 10**6 bits).
    report = BenchmarkReport((Measurement(bytes_received=2_000_000, elapsed_seconds=1.0),))

    assert report.speed_mbit_per_second == pytest.approx(16.0)


def test_speed_is_total_over_total_not_mean_of_speeds() -> None:
    fast_small = Measurement(bytes_received=1_000_000, elapsed_seconds=0.1)  # 80 Mbit/s
    slow_large = Measurement(bytes_received=9_000_000, elapsed_seconds=9.0)  # 8 Mbit/s
    report = BenchmarkReport((fast_small, slow_large))

    # 10 MB in 9.1 s; the mean of the two speeds would be 44 Mbit/s.
    assert report.speed_mbit_per_second == pytest.approx(80.0 / 9.1)
