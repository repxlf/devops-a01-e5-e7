#!/usr/bin/env python3
"""Report whether the local E3 Linux/Docker prerequisites are available.

This script never pulls images, starts containers, or labels a run as verified.
"""

from __future__ import annotations

import argparse
import json
import platform
import shutil
import subprocess
import sys


def version(name: str) -> dict[str, object]:
    executable = shutil.which(name)
    if not executable:
        return {"name": name, "available": False, "version": None}
    try:
        result = subprocess.run([executable, "--version"], capture_output=True, text=True, check=False)
    except OSError:
        return {"name": name, "available": False, "version": None}
    text = (result.stdout or result.stderr).strip().splitlines()
    return {"name": name, "available": result.returncode == 0, "version": text[0] if text else None}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--require-docker", action="store_true")
    args = parser.parse_args()
    tools = [version(name) for name in ("docker", "make", "mingw32-make", "cc", "strace", "python3")]
    make_ready = any(item["available"] for item in tools if item["name"] in {"make", "mingw32-make"})
    result = {
        "provenance": "MOCK_FIXTURE",
        "platform": platform.platform(),
        "tools": tools,
        "docker_required": args.require_docker,
        "ready": make_ready and all(item["available"] for item in tools if item["name"] in {"cc", "python3"}) and (not args.require_docker or tools[0]["available"]),
        "note": "Readiness is not a successful E3 experiment. Run scripts/run_lab.py on Linux and retain its observations.",
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["ready"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
