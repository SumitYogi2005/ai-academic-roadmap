"""
Study plan scheduling algorithm.
Purely deterministic Python — no LLM involvement in scheduling decisions.
"""
from __future__ import annotations

import logging
from collections import defaultdict, deque
from datetime import date, datetime, timedelta
from typing import Any

logger = logging.getLogger(__name__)

DAY_NAMES = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]


def calculate_feasibility(available_minutes: int, required_minutes: int) -> dict:
    """Check whether *required_minutes* fits within *available_minutes*."""
    if available_minutes >= required_minutes:
        return {"feasible": True, "available_minutes": available_minutes, "required_minutes": required_minutes}
    return {
        "feasible": False,
        "available_minutes": available_minutes,
        "required_minutes": required_minutes,
        "deficit_minutes": required_minutes - available_minutes,
        "alternatives": [
            "Extend the target date to allow more study time.",
            "Increase daily study hours in your availability settings.",
            "Remove lower-priority topics from the roadmap.",
        ],
    }


def _topological_sort(node_ids: list[str], prerequisite_edges: list[tuple[str, str]]) -> list[str]:
    """
    Return nodes in topological order (prerequisites first).
    Uses Kahn's algorithm. Nodes with cycles or missing deps are appended last.
    """
    in_degree: dict[str, int] = {n: 0 for n in node_ids}
    adj: dict[str, list[str]] = {n: [] for n in node_ids}

    for src, tgt in prerequisite_edges:
        if src in in_degree and tgt in in_degree:
            adj[src].append(tgt)
            in_degree[tgt] += 1

    queue = deque(n for n in node_ids if in_degree[n] == 0)
    ordered: list[str] = []

    while queue:
        node = queue.popleft()
        ordered.append(node)
        for neighbour in adj[node]:
            in_degree[neighbour] -= 1
            if in_degree[neighbour] == 0:
                queue.append(neighbour)

    # Append any remaining nodes (cycle participants)
    remaining = [n for n in node_ids if n not in set(ordered)]
    ordered.extend(remaining)
    return ordered


def _minutes_for_date(d: date, availability: dict[str, int]) -> int:
    day_name = DAY_NAMES[d.weekday()]
    return availability.get(day_name, 0)


def generate_study_plan(
    nodes: list[dict],
    edges: list[dict],
    start_date: date,
    target_date: date,
    availability: dict[str, int],
) -> dict:
    """
    Generate study sessions for the given roadmap within the date range.

    Parameters
    ----------
    nodes:        list of node dicts with keys: _id (str), title, duration_hours
    edges:        list of edge dicts with keys: source_node_id, target_node_id, relationship_type
    start_date:   first day of the plan
    target_date:  exam / deadline date
    availability: dict mapping day name -> minutes available (e.g. {"monday": 120})

    Returns
    -------
    dict with keys: sessions (list), feasibility_report (dict)
    """
    if not nodes:
        return {"sessions": [], "feasibility_report": {"feasible": True, "note": "No nodes to schedule"}}

    node_ids = [str(n["_id"]) for n in nodes]
    node_map = {str(n["_id"]): n for n in nodes}

    # Build prerequisite pairs
    prereq_pairs: list[tuple[str, str]] = [
        (str(e["source_node_id"]), str(e["target_node_id"]))
        for e in edges
        if e.get("relationship_type") == "prerequisite"
    ]

    ordered_ids = _topological_sort(node_ids, prereq_pairs)

    # Calculate totals
    total_days = (target_date - start_date).days + 1
    available_minutes = sum(
        _minutes_for_date(start_date + timedelta(days=i), availability)
        for i in range(total_days)
    )
    # Add 15% revision buffer
    base_required = sum(int(node_map[n]["duration_hours"] * 60) for n in ordered_ids if n in node_map)
    revision_minutes = int(base_required * 0.15)
    required_minutes = base_required + revision_minutes

    feasibility = calculate_feasibility(available_minutes, required_minutes)

    sessions: list[dict] = []
    current_day = start_date
    day_used: dict[date, int] = defaultdict(int)

    for node_id in ordered_ids:
        if node_id not in node_map:
            continue
        node = node_map[node_id]
        remaining_node_minutes = int(float(node.get("duration_hours", 1.0)) * 60)

        while remaining_node_minutes > 0 and current_day <= target_date:
            day_capacity = _minutes_for_date(current_day, availability)
            day_remaining = day_capacity - day_used[current_day]

            if day_remaining <= 0:
                current_day += timedelta(days=1)
                continue

            session_duration = min(remaining_node_minutes, day_remaining, 120)  # max 2h per session
            if session_duration < 15:
                current_day += timedelta(days=1)
                continue

            sessions.append({
                "node_id": node_id,
                "session_date": current_day.isoformat(),
                "start_time": _suggest_start_time(day_used[current_day]),
                "duration_minutes": session_duration,
                "session_type": _session_type(node),
                "status": "pending",
                "title": node.get("title", "Study Session"),
            })
            day_used[current_day] += session_duration
            remaining_node_minutes -= session_duration

            if day_used[current_day] >= day_capacity:
                current_day += timedelta(days=1)

        if remaining_node_minutes > 0 and current_day > target_date:
            logger.warning("Node %s could not be fully scheduled before target date", node_id)

    logger.info("Scheduled %d sessions across %d days", len(sessions), len(day_used))
    return {
        "sessions": sessions,
        "feasibility_report": feasibility,
        "stats": {
            "total_sessions": len(sessions),
            "scheduled_days": len(day_used),
            "available_minutes": available_minutes,
            "required_minutes": required_minutes,
        },
    }


def reschedule_plan(
    remaining_sessions: list[dict],
    start_from: date,
    target_date: date,
    availability: dict[str, int],
) -> list[dict]:
    """
    Reschedule pending/missed sessions starting from *start_from*.
    Completed sessions are not moved.
    """
    pending = [s for s in remaining_sessions if s.get("status") in ("pending", "missed", "rescheduled")]
    day_used: dict[date, int] = defaultdict(int)
    current_day = start_from
    new_sessions: list[dict] = []

    for session in pending:
        remaining = session["duration_minutes"]
        while remaining > 0 and current_day <= target_date:
            day_cap = _minutes_for_date(current_day, availability)
            day_rem = day_cap - day_used[current_day]
            if day_rem <= 0:
                current_day += timedelta(days=1)
                continue
            alloc = min(remaining, day_rem, 120)
            if alloc < 15:
                current_day += timedelta(days=1)
                continue
            new_sessions.append({
                **session,
                "session_date": current_day.isoformat(),
                "start_time": _suggest_start_time(day_used[current_day]),
                "duration_minutes": alloc,
                "status": "rescheduled",
            })
            day_used[current_day] += alloc
            remaining -= alloc
            if day_used[current_day] >= day_cap:
                current_day += timedelta(days=1)

    return new_sessions


def _suggest_start_time(minutes_already_used: int) -> str:
    """Suggest a start time (HH:MM) based on how much of the day is used."""
    base_hour = 9 + (minutes_already_used // 60)
    base_min = minutes_already_used % 60
    if base_hour >= 22:
        base_hour = 20
        base_min = 0
    return f"{base_hour:02d}:{base_min:02d}"


def _session_type(node: dict) -> str:
    node_type = node.get("type", "concept")
    return {
        "concept": "study",
        "practice": "practice",
        "project": "project",
        "assessment": "assessment",
    }.get(node_type, "study")
