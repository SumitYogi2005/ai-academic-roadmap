"""
Authentication routes: register, login, refresh token.
"""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.core.security import (
    create_access_token,
    create_refresh_token,
    hash_password,
    verify_password,
    verify_refresh_token,
    get_current_user_id,
)
from app.core.config import settings
from app.db.database import get_database
from app.models.user import UserDocument
from app.repositories import user_repository as user_repo
from app.schemas.auth import LoginRequest, RefreshRequest, RegisterRequest, TokenResponse, UserResponse, UserPreferencesResponse

router = APIRouter(prefix="/auth", tags=["Authentication"])


def _user_to_response(user: dict) -> UserResponse:
    prefs = user.get("preferences", {})
    return UserResponse(
        id=user["_id"],
        full_name=user["full_name"],
        email=user["email"],
        preferences=UserPreferencesResponse(
            study_hours_per_day=prefs.get("study_hours_per_day", 2.0),
            preferred_study_times=prefs.get("preferred_study_times", ["morning"]),
            learning_level=prefs.get("learning_level", "beginner"),
            goal=prefs.get("goal", ""),
        ),
        is_active=user.get("is_active", True),
        created_at=user["created_at"],
    )


def _build_token_response(user: dict) -> dict:
    user_id = user["_id"]
    access_token = create_access_token(user_id)
    refresh_token = create_refresh_token(user_id)
    return {
        "success": True,
        "data": TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=settings.access_token_expire_seconds,
            user=_user_to_response(user),
        ).model_dump(),
        "message": "Authentication successful",
    }


@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register(
    body: RegisterRequest,
    db: AsyncIOMotorDatabase = Depends(get_database),
):
    """Register a new student account."""
    email = body.email.lower().strip()
    if await user_repo.email_exists(db, email):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="An account with this email already exists.",
        )
    user_doc = UserDocument(
        full_name=body.full_name.strip(),
        email=email,
        password_hash=hash_password(body.password),
    )
    user = await user_repo.create_user(db, user_doc)
    return _build_token_response(user)


@router.post("/login", status_code=status.HTTP_200_OK)
async def login(
    body: LoginRequest,
    db: AsyncIOMotorDatabase = Depends(get_database),
):
    """Authenticate with email and password, return JWT tokens."""
    email = body.email.lower().strip()
    user = await user_repo.get_user_by_email(db, email)
    if not user or not verify_password(body.password, user.get("password_hash", "")):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password.",
        )
    if not user.get("is_active", True):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is deactivated.",
        )
    return _build_token_response(user)


@router.post("/refresh", status_code=status.HTTP_200_OK)
async def refresh_token(
    body: RefreshRequest,
    db: AsyncIOMotorDatabase = Depends(get_database),
):
    """Exchange a refresh token for a new access token."""
    user_id = verify_refresh_token(body.refresh_token)
    user = await user_repo.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found.")
    return _build_token_response(user)
