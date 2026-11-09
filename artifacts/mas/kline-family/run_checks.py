"""Run the same memo013 acceptance tests against one preserved implementation."""

import argparse
import json
import os
import subprocess
from datetime import UTC, datetime
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("variant", choices=("baseline", "python_pro", "active"))
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[3]
    evidence = Path(__file__).resolve().parent
    implementation = (
        root / "src" if args.variant == "active" else evidence / args.variant
    )
    environment = dict(
        os.environ, PYTHONPATH=os.pathsep.join((str(implementation), str(root / "src")))
    )
    python = str(root / ".venv/bin/python")
    identity = subprocess.run(
        [
            python,
            "-c",
            "from chanlab.algo import kline; from chanlab.data import kline_csv; print(kline.__file__); print(kline_csv.__file__)",
        ],
        check=False,
        cwd=root,
        env=environment,
        capture_output=True,
        text=True,
    )
    if identity.returncode:
        raise RuntimeError(identity.stderr)
    modules = identity.stdout.splitlines()
    if len(modules) != 2 or any(
        not Path(item).is_relative_to(implementation) for item in modules
    ):
        raise RuntimeError(f"wrong implementation imported: {modules}")
    command = [
        python,
        "-m",
        "pytest",
        "tests/test_kline_family.py",
        "tests/test_kline_csv.py",
        "-q",
    ]
    result = subprocess.run(
        command, check=False, cwd=root, env=environment, capture_output=True, text=True
    )
    checks = evidence / "checks"
    checks.mkdir(exist_ok=True)
    (checks / f"{args.variant}-pytest.txt").write_text(result.stdout + result.stderr)
    report = {
        "variant": args.variant,
        "checked_at": datetime.now(UTC).isoformat(),
        "command": command,
        "PYTHONPATH": environment["PYTHONPATH"],
        "modules": modules,
        "returncode": result.returncode,
        "output": result.stdout + result.stderr,
    }
    (checks / f"{args.variant}-pytest.json").write_text(
        json.dumps(report, indent=2) + "\n"
    )
    print(result.stdout, end="")
    print(result.stderr, end="")
    return result.returncode


if __name__ == "__main__":
    raise SystemExit(main())
