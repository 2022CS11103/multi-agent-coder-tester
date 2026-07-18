"""
main.py
-------
Command-line entry point. Give the team a coding task in plain English,
and watch the Coder + Tester agents work (with your approval) to solve it.

Usage:
    python -m src.main "write a function that checks if a number is prime"
"""

import sys
from src.graph import run_team


def main():
    if len(sys.argv) > 1:
        task = " ".join(sys.argv[1:])
    else:
        task = input("Describe the coding task for the team: ").strip()

    if not task:
        print("No task given, exiting.")
        return

    run_team(task)


if __name__ == "__main__":
    main()
