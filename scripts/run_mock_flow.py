"""Print the contract-only end-to-end flow represented by the fixtures."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    scenario_path = ROOT / "examples/end-to-end/scenario.json"
    scenario = json.loads(scenario_path.read_text(encoding="utf-8"))
    print(f"Scenario: {scenario['scenario_id']} ({scenario['provenance']})")
    for index, stage in enumerate(scenario["stages"], start=1):
        owner = stage["owner"]
        references = [
            value
            for key, value in stage.items()
            if key in {"input", "job", "artifacts", "result"}
        ]
        print(f"{index}. {stage['name']} [{owner}] -> {references}")
    print("Mock flow complete: no real build or dependency analyzer was executed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
