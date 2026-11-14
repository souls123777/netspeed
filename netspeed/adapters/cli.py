"""Driving adapter: turns command-line input into a use-case call and prints the result."""

import argparse
import sys
from collections.abc import Sequence

from netspeed import constants
from netspeed.domain import BenchmarkReport
from netspeed.ports import Downloader, DownloadError
from netspeed.use_case import run_benchmark


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog=constants.PROGRAM_NAME, description=constants.CLI_DESCRIPTION
    )
    parser.add_argument("url", help=constants.CLI_URL_HELP)
    return parser


def format_report(url: str, report: BenchmarkReport) -> str:
    return constants.REPORT_TEMPLATE.format(
        url=url,
        requests=report.requests_count,
        size=report.total_bytes / constants.BYTES_PER_MEGABYTE,
        size_unit=constants.SIZE_UNIT,
        total_bytes=report.total_bytes,
        total_time=report.total_seconds,
        average_time=report.average_request_seconds,
        time_unit=constants.TIME_UNIT,
        speed=report.speed_mbit_per_second,
        speed_unit=constants.SPEED_UNIT,
    )


def run(argv: Sequence[str], downloader: Downloader) -> int:
    """Run the CLI and return the process exit code."""
    args = build_parser().parse_args(argv)
    try:
        report = run_benchmark(downloader, args.url)
    except DownloadError as error:
        print(constants.ERROR_TEMPLATE.format(message=error), file=sys.stderr)
        return constants.EXIT_CODE_FAILURE
    except KeyboardInterrupt:
        print(constants.INTERRUPTED_MESSAGE, file=sys.stderr)
        return constants.EXIT_CODE_INTERRUPTED
    print(format_report(args.url, report))
    return constants.EXIT_CODE_OK
