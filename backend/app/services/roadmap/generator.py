"""
Roadmap generation service.
Generates academic and skill roadmaps, validates structures.
"""
from __future__ import annotations

import logging
from typing import Any

from app.models.roadmap import NodeType, NodeDifficulty, EdgeRelationship
from app.services.ai.provider import get_ai_provider
from app.services.ai.prompts import academic_roadmap_prompt, skill_roadmap_prompt

logger = logging.getLogger(__name__)


def detect_prerequisite_cycles(edges: list[dict]) -> bool:
    """Return True if the prerequisite graph contains a cycle (using DFS)."""
    graph: dict[str, list[str]] = {}
    for edge in edges:
        if edge.get("relationship_type") == "prerequisite":
            src = edge["source_node_id"]
            tgt = edge["target_node_id"]
            graph.setdefault(src, []).append(tgt)

    visited: set[str] = set()
    rec_stack: set[str] = set()

    def dfs(node: str) -> bool:
        visited.add(node)
        rec_stack.add(node)
        for neighbour in graph.get(node, []):
            if neighbour not in visited:
                if dfs(neighbour):
                    return True
            elif neighbour in rec_stack:
                return True
        rec_stack.discard(node)
        return False

    for node in list(graph.keys()):
        if node not in visited:
            if dfs(node):
                return True
    return False


def _clamp_node_type(value: str) -> str:
    valid = {t.value for t in NodeType}
    return value if value in valid else NodeType.CONCEPT.value


def _clamp_difficulty(value: str) -> str:
    valid = {d.value for d in NodeDifficulty}
    return value if value in valid else NodeDifficulty.BEGINNER.value


def _layout_positions(nodes: list[dict]) -> list[dict]:
    """Assign grid-based positions if the model didn't provide them."""
    cols = 3
    for i, node in enumerate(nodes):
        if node.get("position_x", 0) == 0 and node.get("position_y", 0) == 0:
            col = i % cols
            row = i // cols
            node["position_x"] = float(col * 250 + 100)
            node["position_y"] = float(row * 180 + 100)
    return nodes


async def generate_academic_roadmap(
    syllabus_data: dict,
    roadmap_id: str,
) -> tuple[list[dict], list[dict]]:
    """
    Call AI to generate roadmap nodes/edges from verified syllabus data.
    Returns (nodes_dicts, edges_dicts) ready for DB insertion.
    """
    provider = get_ai_provider()
    prompt = academic_roadmap_prompt(syllabus_data)

    try:
        result = await provider.generate_structured_output(prompt, schema={})
    except Exception as exc:
        logger.error("Academic roadmap AI call failed: %s", exc)
        # Return minimal stub roadmap
        result = _stub_academic_roadmap(syllabus_data)

    raw_nodes: list[dict] = result.get("nodes", [])
    raw_edges: list[dict] = result.get("edges", [])

    # Build a lookup from source_topic_id -> node index
    topic_to_index: dict[str, int] = {}
    for i, n in enumerate(raw_nodes):
        if n.get("source_topic_id"):
            topic_to_index[n["source_topic_id"]] = i

    # Assign positions if missing
    raw_nodes = _layout_positions(raw_nodes)

    # Convert to DB-ready dicts (without _id; that's added on insert)
    nodes = []
    for n in raw_nodes:
        nodes.append({
            "roadmap_id": roadmap_id,
            "title": n.get("title", "Untitled Node"),
            "description": n.get("description", ""),
            "type": _clamp_node_type(n.get("type", "concept")),
            "duration_hours": float(n.get("duration_hours", 1.0)),
            "difficulty": _clamp_difficulty(n.get("difficulty", "beginner")),
            "source_topic_id": n.get("source_topic_id"),
            "position_x": float(n.get("position_x", 0)),
            "position_y": float(n.get("position_y", 0)),
        })

    edges_raw = []
    for e in raw_edges:
        src_tid = e.get("source_topic_id", "")
        tgt_tid = e.get("target_topic_id", "")
        edges_raw.append({
            "roadmap_id": roadmap_id,
            "source_topic_id": src_tid,
            "target_topic_id": tgt_tid,
            "relationship_type": e.get("relationship_type", "prerequisite"),
        })

    logger.info(
        "Academic roadmap generated: %d nodes, %d edges", len(nodes), len(edges_raw)
    )
    return nodes, edges_raw


async def generate_skill_roadmap(
    skill: str,
    level: str,
    goal: str,
    timeframe_weeks: int,
    roadmap_id: str,
) -> tuple[list[dict], list[dict]]:
    """
    Call AI to generate a skill roadmap.
    Returns (nodes_dicts, edges_dicts) ready for DB insertion.
    """
    provider = get_ai_provider()
    prompt = skill_roadmap_prompt(skill, level, goal, timeframe_weeks)

    try:
        result = await provider.generate_structured_output(prompt, schema={})
    except Exception as exc:
        logger.error("Skill roadmap AI call failed: %s", exc)
        result = _stub_skill_roadmap(skill)

    raw_nodes: list[dict] = result.get("nodes", [])
    raw_edges: list[dict] = result.get("edges", [])

    raw_nodes = _layout_positions(raw_nodes)

    nodes = []
    for n in raw_nodes:
        nodes.append({
            "roadmap_id": roadmap_id,
            "title": n.get("title", "Untitled"),
            "description": n.get("description", ""),
            "type": _clamp_node_type(n.get("type", "concept")),
            "duration_hours": float(n.get("duration_hours", 1.0)),
            "difficulty": _clamp_difficulty(n.get("difficulty", "beginner")),
            "source_topic_id": None,
            "position_x": float(n.get("position_x", 0)),
            "position_y": float(n.get("position_y", 0)),
        })

    edges_indexed = []
    for e in raw_edges:
        src_i = e.get("source_index", 0)
        tgt_i = e.get("target_index", 1)
        edges_indexed.append({
            "roadmap_id": roadmap_id,
            "source_index": int(src_i),
            "target_index": int(tgt_i),
            "relationship_type": e.get("relationship_type", "prerequisite"),
        })

    logger.info("Skill roadmap generated: %d nodes, %d edges", len(nodes), len(edges_indexed))
    return nodes, edges_indexed


# ── Stubs for no-AI fallback ──────────────────────────────────────────────────

def _stub_academic_roadmap(syllabus_data: dict) -> dict:
    nodes = []
    edges = []
    for unit in syllabus_data.get("units", []):
        for topic in unit.get("topics", []):
            nodes.append({
                "source_topic_id": topic["id"],
                "title": topic["name"],
                "description": topic.get("description", ""),
                "type": "concept",
                "duration_hours": topic.get("duration_hours", 1.0),
                "difficulty": "beginner",
            })
    # Simple linear edges
    for i in range(len(nodes) - 1):
        edges.append({
            "source_topic_id": nodes[i]["source_topic_id"],
            "target_topic_id": nodes[i + 1]["source_topic_id"],
            "relationship_type": "prerequisite",
        })
    return {"nodes": nodes, "edges": edges}


def _stub_skill_roadmap(skill: str) -> dict:
    stages = ["Fundamentals", "Core Concepts", "Practice Projects", "Advanced Topics", "Capstone"]
    nodes = [
        {"title": f"{skill}: {stage}", "description": f"Learn {stage.lower()} of {skill}",
         "type": "concept", "duration_hours": 3.0, "difficulty": "beginner"}
        for stage in stages
    ]
    edges = [{"source_index": i, "target_index": i + 1, "relationship_type": "prerequisite"}
             for i in range(len(stages) - 1)]
    return {"nodes": nodes, "edges": edges}
