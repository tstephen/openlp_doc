"""
Test runner script for openlp_ctrl
"""

import subprocess
import sys


def test():
    """Run tests with coverage"""
    result = subprocess.run(
        [
            "coverage",
            "run",
            "--omit",
            "*/site-packages/*,tests/*",
            "-m",
            "pytest",
            "tests/",
            "-v",
        ],
        cwd=".",
    )
    sys.exit(result.returncode)


if __name__ == "__main__":
    test()
