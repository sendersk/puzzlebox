"""Run all PuzzleBox quality checks."""

import subprocess
import sys

COMMANDS = (
    ("Ruff check", ("uv", "run", "ruff", "check", ".")),
    (
        "Ruff format",
        ("uv", "run", "ruff", "format", "--check", "."),
    ),
    ("MyPy", ("uv", "run", "mypy", "src")),
    (
        "Tests and coverage",
        (
            "uv",
            "run",
            "pytest",
            "--cov=src/puzzlebox",
            "--cov-report=term-missing",
        ),
    ),
)


def run_check(name: str, command: tuple[str, ...]) -> bool:
    """Run one quality check and return whether it passed."""
    print(f"\n=== {name} ===")

    result = subprocess.run(command, check=False)

    if result.returncode != 0:
        print(f"\n{name} failed.")

        return False

    return True


def main() -> int:
    """Run all quality checks."""
    for name, command in COMMANDS:
        if not run_check(name, command):
            return 1

    print("\nAll quality checks passed.")

    return 0


if __name__ == "__main__":
    sys.exit(main())
