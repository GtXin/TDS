"""Query Codex's local app-server for the repository skill without a model call."""

from __future__ import annotations

import json
import os
from pathlib import Path
import select
import subprocess
import tempfile
import time


def main() -> None:
    """Check the live skill index and save only this skill's discovery evidence."""
    root = Path(__file__).resolve().parents[3]
    expected = root / "mas/skills/python-pro/SKILL.md"
    temporary_home = tempfile.TemporaryDirectory(prefix="tds-skill-index-")
    environment = dict(os.environ, CODEX_HOME=temporary_home.name)
    process = subprocess.Popen(
        ["codex", "app-server", "--stdio"],
        cwd=root,
        env=environment,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    assert process.stdin is not None
    assert process.stdout is not None
    pending = b""

    def send(message: dict[str, object]) -> None:
        process.stdin.write(json.dumps(message).encode() + b"\n")
        process.stdin.flush()

    def response(request_id: int) -> dict[str, object]:
        nonlocal pending
        deadline = time.monotonic() + 25
        while time.monotonic() < deadline:
            while b"\n" in pending:
                line, pending = pending.split(b"\n", 1)
                if not line.strip():
                    continue
                message = json.loads(line)
                if message.get("id") == request_id:
                    if "error" in message:
                        raise RuntimeError(str(message["error"]))
                    return message["result"]
            ready, _, _ = select.select([process.stdout], [], [], 0.2)
            if ready:
                chunk = os.read(process.stdout.fileno(), 65536)
                if not chunk:
                    raise RuntimeError("Codex proxy closed before replying")
                pending += chunk
        raise TimeoutError("Codex skill-list response exceeded 25 seconds")

    try:
        send(
            {
                "id": 1,
                "method": "initialize",
                "params": {
                    "clientInfo": {"name": "tds_skill_check", "version": "1.0"},
                    "capabilities": {"experimentalApi": True},
                },
            }
        )
        response(1)
        send({"method": "initialized", "params": {}})
        send(
            {
                "id": 2,
                "method": "skills/list",
                "params": {"cwds": [str(root)], "forceReload": True},
            }
        )
        result = response(2)
        matches = [
            skill
            for entry in result["data"]
            for skill in entry["skills"]
            if skill["name"] == "python-pro"
            and Path(skill["path"]).resolve() == expected.resolve()
        ]
        errors = [
            error
            for entry in result["data"]
            for error in entry["errors"]
            if "python-pro" in error["path"]
        ]
        assert len(matches) == 1, matches
        assert matches[0]["enabled"] and matches[0]["scope"] == "repo"
        assert not errors, errors
        evidence = {
            "method": "skills/list",
            "forceReload": True,
            "cwd": str(root),
            "skill": matches[0],
            "skill_errors": errors,
            "model_called": False,
            "runtime": "isolated local app-server; repository skills only verified",
        }
        (Path(__file__).parent / "discovery.json").write_text(
            json.dumps(evidence, indent=2) + "\n"
        )
        print(json.dumps({"name": "python-pro", "scope": "repo", "enabled": True}))
    finally:
        process.terminate()
        try:
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait(timeout=5)
        if process.stderr is not None:
            stderr = process.stderr.read().decode(errors="replace")
            (Path(__file__).parent / "discovery-stderr.txt").write_text(stderr)
        temporary_home.cleanup()


if __name__ == "__main__":
    main()
