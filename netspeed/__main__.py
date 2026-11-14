"""Composition root: the only place where ports are bound to concrete adapters."""

import sys

from netspeed.adapters.cli import run
from netspeed.adapters.http_downloader import UrllibDownloader


def main() -> int:
    return run(sys.argv[1:], UrllibDownloader())


if __name__ == "__main__":
    sys.exit(main())
