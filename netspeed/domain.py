"""Domain model: what one measurement is and how a whole run is summarised.

Pure Python with no I/O, so everything here is testable without a network.
"""

from dataclasses import dataclass

from netspeed import constants


@dataclass(frozen=True, slots=True)
class Measurement:
    """Outcome of one download that was read to the last byte."""

    bytes_received: int
    elapsed_seconds: float

    def __post_init__(self) -> None:
        if self.bytes_received < 0:
            raise ValueError(constants.NEGATIVE_BYTES_MESSAGE)
        if self.elapsed_seconds <= 0:
            raise ValueError(constants.NON_POSITIVE_TIME_MESSAGE)


@dataclass(frozen=True, slots=True)
class BenchmarkReport:
    """All measurements of a run plus the figures derived from them."""

    measurements: tuple[Measurement, ...]

    def __post_init__(self) -> None:
        if not self.measurements:
            raise ValueError(constants.EMPTY_REPORT_MESSAGE)

    @property
    def requests_count(self) -> int:
        return len(self.measurements)

    @property
    def total_bytes(self) -> int:
        return sum(m.bytes_received for m in self.measurements)

    @property
    def total_seconds(self) -> float:
        return sum(m.elapsed_seconds for m in self.measurements)

    @property
    def average_request_seconds(self) -> float:
        return self.total_seconds / self.requests_count

    @property
    def speed_mbit_per_second(self) -> float:
        """Total bits over total time.

        Deliberately not the mean of per-request speeds: that would let a small,
        fast request weigh as much as a large, slow one.
        """
        total_bits = self.total_bytes * constants.BITS_PER_BYTE
        return total_bits / self.total_seconds / constants.BITS_PER_MEGABIT
