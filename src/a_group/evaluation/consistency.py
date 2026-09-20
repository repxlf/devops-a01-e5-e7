from collections.abc import Mapping, Sequence


def edge_key(edge: Mapping[str, object]) -> tuple[str, str]:
    return str(edge.get("source", "")), str(edge.get("target", ""))


def compare_graphs(incremental: Mapping[str, object], full: Mapping[str, object]) -> bool:
    incremental_edges = {edge_key(edge) for edge in incremental.get("edges", [])}  # type: ignore[arg-type]
    full_edges = {edge_key(edge) for edge in full.get("edges", [])}  # type: ignore[arg-type]
    return incremental_edges == full_edges


def compare_finding_ids(incremental: Sequence[Mapping[str, object]], full: Sequence[Mapping[str, object]]) -> bool:
    return {str(item.get("finding_id")) for item in incremental} == {
        str(item.get("finding_id")) for item in full
    }
