"""
Planner service unit tests.
"""
import pytest
from datetime import date, timedelta


class TestFeasibilityCheck:
    """Tests for study plan feasibility calculation."""

    def test_feasible_plan(self):
        """Should return feasible when enough time available."""
        from app.services.planner.scheduler import calculate_feasibility
        result = calculate_feasibility(
            available_minutes=1200,
            required_minutes=900
        )
        assert result["feasible"] is True

    def test_infeasible_plan(self):
        """Should return infeasible with alternatives when time is insufficient."""
        from app.services.planner.scheduler import calculate_feasibility
        result = calculate_feasibility(
            available_minutes=500,
            required_minutes=900
        )
        assert result["feasible"] is False
        assert "deficit_minutes" in result

    def test_exact_capacity(self):
        """Should be feasible when available exactly equals required."""
        from app.services.planner.scheduler import calculate_feasibility
        result = calculate_feasibility(
            available_minutes=900,
            required_minutes=900
        )
        assert result["feasible"] is True


class TestSchedulerNoCapacityViolations:
    """Test that scheduler never exceeds daily capacity."""

    def test_no_daily_overflow(self):
        """Sessions on any day should not exceed available minutes."""
        from app.services.planner.scheduler import generate_study_plan

        nodes = [
            {"_id": "n1", "title": "Topic A", "duration_hours": 2.0, "difficulty": "easy", "type": "concept"},
            {"_id": "n2", "title": "Topic B", "duration_hours": 1.5, "difficulty": "medium", "type": "concept"},
            {"_id": "n3", "title": "Topic C", "duration_hours": 1.0, "difficulty": "easy", "type": "practice"},
        ]
        edges = []  # No prerequisites

        availability = {
            "monday": 120,
            "tuesday": 90,
            "wednesday": 120,
            "thursday": 90,
            "friday": 60,
            "saturday": 180,
            "sunday": 0,
        }

        start = date.today()
        target = start + timedelta(days=14)

        plan = generate_study_plan(
            nodes=nodes,
            edges=edges,
            start_date=start,
            target_date=target,
            availability=availability,
        )

        # Group sessions by date and check capacity
        from collections import defaultdict
        sessions_by_date = defaultdict(list)
        for session in plan["sessions"]:
            sessions_by_date[session["session_date"]].append(session)

        day_names = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
        for day_str, sessions in sessions_by_date.items():
            day_obj = date.fromisoformat(day_str) if isinstance(day_str, str) else day_str
            day_name = day_names[day_obj.weekday()]
            total = sum(s["duration_minutes"] for s in sessions)
            assert total <= availability[day_name], \
                f"Day {day_str} used {total}m but only {availability[day_name]}m available"
