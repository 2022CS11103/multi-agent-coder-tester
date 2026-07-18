"""
sandbox.py
----------
Runs the Coder's code + Tester's tests INSIDE a throwaway Docker
container instead of directly on your machine. This matters because
the code is AI-generated — you don't want to blindly execute unknown
code on your real computer. Docker keeps it isolated.

Requires Docker Desktop to be running.
"""

import os
import shutil
import subprocess
import tempfile

from src.config import SANDBOX_IMAGE, EXECUTION_TIMEOUT


def run_in_docker(solution_code: str, test_code: str) -> dict:
    """
    Writes solution.py + test_solution.py into a temp folder, then runs
    `python -m unittest test_solution.py` inside a fresh, disposable
    Docker container that can only see that temp folder.

    Returns: {"passed": bool, "output": str}
    """
    temp_dir = tempfile.mkdtemp(prefix="agent_sandbox_")
    try:
        with open(os.path.join(temp_dir, "solution.py"), "w", encoding="utf-8") as f:
            f.write(solution_code)
        with open(os.path.join(temp_dir, "test_solution.py"), "w", encoding="utf-8") as f:
            f.write(test_code)

        # Docker must be installed & running for this to work.
        docker_cmd = [
            "docker", "run", "--rm",
            "--network", "none",              # no internet access inside container = extra safety
            "--memory", "256m",
            "-v", f"{temp_dir}:/sandbox:ro",   # mount code as READ-ONLY
            "-w", "/sandbox",
            SANDBOX_IMAGE,
            "python", "-m", "unittest", "test_solution.py", "-v",
        ]

        try:
            result = subprocess.run(
                docker_cmd,
                capture_output=True,
                text=True,
                timeout=EXECUTION_TIMEOUT,
            )
        except subprocess.TimeoutExpired:
            return {"passed": False, "output": f"Execution timed out after {EXECUTION_TIMEOUT}s (possible infinite loop)."}
        except FileNotFoundError:
            return {"passed": False, "output": "ERROR: Docker not found. Is Docker Desktop installed and running?"}

        combined_output = (result.stdout or "") + "\n" + (result.stderr or "")
        passed = result.returncode == 0
        return {"passed": passed, "output": combined_output.strip()}

    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)


def save_final_files(solution_code: str, test_code: str, out_dir: str):
    """Save the final approved solution + tests to disk for the user to keep."""
    os.makedirs(out_dir, exist_ok=True)
    with open(os.path.join(out_dir, "solution.py"), "w", encoding="utf-8") as f:
        f.write(solution_code)
    with open(os.path.join(out_dir, "test_solution.py"), "w", encoding="utf-8") as f:
        f.write(test_code)
