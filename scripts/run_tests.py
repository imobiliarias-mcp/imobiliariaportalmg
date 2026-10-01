"""Automated test suite runner."""

import sys
import pytest


def main() -> None:
    """Execute pytest test runner."""
    args = sys.argv[1:] or ["-v", "tests/"]
    exit_code = pytest.main(args)
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
