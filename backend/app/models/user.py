"""
Pydantic models for the `users` MongoDB collection.
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import List, Optional

from pydantic import BaseModel, EmailStr, Field


# ── Embedded sub-models ───────────────────────────────────────────────────────

class UserPreferences(BaseModel):
    """Embedded document storing a user's study preferences."""
    study_hours_per_day: float = Field(default=2.0, ge=0.5, le=24.0)
    preferred_study_times: List[str] = Field(
        default_factory=lambda: ["morning"],
        description="E.g. ['morning', 'evening']",
    )
    learning_level: str = Field(
        default="beginner",
        description="One of: beginner, intermediate, advanced",
    )
    goal: str = Field(default="", description="User's primary learning goal")


# ── Top-level document ────────────────────────────────────────────────────────

class UserDocument(BaseModel):
    """Represents a user document in the `users` collection."""

    id: Optional[str] = Field(default=None, alias="_id")
    full_name: str
    email: EmailStr
    password_hash: str
    preferences: UserPreferences = Field(default_factory=UserPreferences)
    is_active: bool = True
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    model_config = {"populate_by_name": True}

    def to_mongo(self) -> dict:
        """Serialise for MongoDB insertion (excludes `id`, keeps `_id` as None so Mongo generates it)."""
        data = self.model_dump(by_alias=True, exclude_none=True)
        data.pop("_id", None)  # let MongoDB generate _id
        return data
