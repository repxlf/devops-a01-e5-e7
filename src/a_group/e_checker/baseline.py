"""Baseline validation kept separate from graph-diff logic."""

from typing import Any, Mapping


def validate_baseline(input_value: Mapping[str, Any]) -> None:
    baseline = input_value.get("baseline")
    if not isinstance(baseline, Mapping):
        raise ValueError("INCREMENTAL_CHECK requires baseline")
    if baseline.get("commit") != input_value.get("base_commit"):
        raise ValueError("baseline.commit must match base_commit")
    current_configuration = input_value.get("environment", {}).get("configuration_id")
    if current_configuration and baseline.get("configuration_id") != current_configuration:
        raise ValueError("baseline.configuration_id must match current configuration")
