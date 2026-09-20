"""Pure helpers for comparing finding identities."""

from collections.abc import Iterable, Mapping


def finding_key(finding: Mapping[str, object]) -> str:
    return str(finding.get("finding_id") or "|".join(
        str(finding.get(field, ""))
        for field in ("type", "target", "dependency", "commit")
    ))


def diff_findings(
    baseline: Iterable[Mapping[str, object]],
    current: Iterable[Mapping[str, object]],
) -> tuple[list[Mapping[str, object]], list[Mapping[str, object]]]:
    baseline_map = {finding_key(item): item for item in baseline}
    current_map = {finding_key(item): item for item in current}
    added = [value for key, value in current_map.items() if key not in baseline_map]
    resolved = [value for key, value in baseline_map.items() if key not in current_map]
    return added, resolved
