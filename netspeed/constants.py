"""Every number, string and unit used by the tool lives here."""

# --- Benchmark ---------------------------------------------------------------
REQUESTS_COUNT = 10

# --- Program identity --------------------------------------------------------
PROGRAM_NAME = "netspeed"
PROGRAM_VERSION = "1.0"

# --- HTTP --------------------------------------------------------------------
USER_AGENT = f"{PROGRAM_NAME}/{PROGRAM_VERSION}"
HEADER_USER_AGENT = "User-Agent"
HEADER_CONTENT_LENGTH = "Content-Length"
ALLOWED_URL_SCHEMES = ("http", "https")
ALLOWED_URL_SCHEMES_TEXT = ", ".join(ALLOWED_URL_SCHEMES)
# Applies to each socket operation (connect, read), not to the download as a whole.
REQUEST_TIMEOUT_SECONDS = 30.0
BYTES_PER_KIB = 1024
READ_CHUNK_SIZE_BYTES = 64 * BYTES_PER_KIB

# --- Units -------------------------------------------------------------------
BITS_PER_BYTE = 8
BITS_PER_MEGABIT = 1_000_000
BYTES_PER_MEGABYTE = 1_000_000
SPEED_UNIT = "Mbit/s"
SIZE_UNIT = "MB"
TIME_UNIT = "s"

# --- Exit codes --------------------------------------------------------------
EXIT_CODE_OK = 0
EXIT_CODE_FAILURE = 1
EXIT_CODE_INTERRUPTED = 130

# --- CLI text ----------------------------------------------------------------
CLI_DESCRIPTION = (
    "Measure download speed: request a URL several times in a row, "
    "wait for each response body in full, and report the result."
)
CLI_URL_HELP = "address to download from (http or https), e.g. a large image"

REPORT_TEMPLATE = (
    "URL:                  {url}\n"
    "Requests:             {requests}\n"
    "Total downloaded:     {size:.2f} {size_unit} ({total_bytes} bytes)\n"
    "Total time:           {total_time:.3f} {time_unit}\n"
    "Average request time: {average_time:.3f} {time_unit}\n"
    "Download speed:       {speed:.2f} {speed_unit}"
)
ERROR_TEMPLATE = "error: {message}"
INTERRUPTED_MESSAGE = "interrupted"

# --- Error messages ----------------------------------------------------------
REQUEST_FAILED_TEMPLATE = "request {number} of {total} failed: {reason}"
DOWNLOAD_FAILED_TEMPLATE = "{url}: {reason}"
UNSUPPORTED_SCHEME_TEMPLATE = "unsupported URL scheme {scheme!r} (expected: {allowed})"
INCOMPLETE_RESPONSE_TEMPLATE = (
    "incomplete response: expected {expected} bytes, received {received}"
)
NEGATIVE_BYTES_MESSAGE = "bytes_received must not be negative"
NON_POSITIVE_TIME_MESSAGE = "elapsed_seconds must be positive"
EMPTY_REPORT_MESSAGE = "a report needs at least one measurement"
