"""Authentication API endpoints."""

from datetime import datetime, timezone

import jwt
from fastapi import APIRouter, HTTPException
from peewee import IntegrityError
from pydantic import BaseModel, EmailStr

from src.config import settings
from src.users.models import User


# Authentication models
class RegisterRequest(BaseModel):
    """Request model for user registration."""

    username: str
    email: EmailStr
    password: str


class LoginRequest(BaseModel):
    """Request model for user login."""

    username: str
    password: str


class AuthResponse(BaseModel):
    """Response model for authentication endpoints."""

    access_token: str
    token_type: str = "bearer"
    user: dict


# JWT utility functions
def create_access_token(user_id: int, username: str) -> str:
    """Create a JWT access token without expiration."""
    payload = {
        "username": username,
        "iat": datetime.now(timezone.utc),
    }
    token = jwt.encode(payload, settings.jwt_secret, algorithm="HS256")
    return token


# Create auth router
auth_router = APIRouter(prefix="/api", tags=["auth"])


# Authentication endpoints
@auth_router.post("/register", response_model=AuthResponse)
async def register(request: RegisterRequest) -> AuthResponse:
    """Register a new user."""
    try:
        # Create new user
        user = User(username=request.username, email=request.email)
        user.set_password(request.password)
        user.save()

        # Generate JWT token
        access_token = create_access_token(user_id=user.id, username=user.username)

        return AuthResponse(
            access_token=access_token,
            user={
                "username": user.username,
                "email": user.email,
            },
        )
    except IntegrityError as e:
        error_msg = str(e).lower()
        if "username" in error_msg:
            raise HTTPException(status_code=400, detail="Username already exists") from None
        elif "email" in error_msg:
            raise HTTPException(status_code=400, detail="Email already exists") from None
        else:
            raise HTTPException(status_code=400, detail="User already exists") from None


@auth_router.post("/login", response_model=AuthResponse)
async def login(request: LoginRequest) -> AuthResponse:
    """Login a user and return a JWT token."""
    try:
        # Find user by username
        user = User.get(User.username == request.username)
    except User.DoesNotExist:
        raise HTTPException(status_code=401, detail="Invalid username or password") from None

    # Verify password
    if not user.verify_password(request.password):
        raise HTTPException(status_code=401, detail="Invalid username or password")

    # Generate JWT token
    access_token = create_access_token(user_id=user.id, username=user.username)

    return AuthResponse(
        access_token=access_token,
        user={
            "username": user.username,
            "email": user.email,
        },
    )
