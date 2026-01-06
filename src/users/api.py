"""Authentication API endpoints."""

import base64
import logging
import random
import string
from datetime import UTC, datetime, timedelta

import jwt
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, EmailStr
from cryptography.fernet import Fernet

from src.config import settings
from src.email_service import send_login_code_email
from src.users.models import User

logger = logging.getLogger(__name__)


class EmailLoginRequest(BaseModel):
    """Request model for initiating email-based login."""

    email: EmailStr

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "email": "user@example.com"
                }
            ]
        }
    }


class Email2LoginRequest(BaseModel):
    """Request model for verifying email login code."""

    email: EmailStr
    email_code: str
    token: str

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "email": "user@example.com",
                    "email_code": "123456",
                    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
                }
            ]
        }
    }


class EmailAuthResponse(BaseModel):
    """Response containing encrypted token for email verification."""

    token: str
    email_token_valid_until: datetime

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                    "email_token_valid_until": "2025-12-31T12:05:00"
                }
            ]
        }
    }


class AuthResponse(BaseModel):
    """Response containing JWT access token for authenticated requests."""

    access_token: str
    token_type: str = "bearer"
    token_valid_until: datetime | None = None

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJlbWFpbCI6InVzZXJAZXhhbXBsZS5jb20iLCJpYXQiOjE3MDM5NjY0MDB9...",
                    "token_type": "bearer"
                }
            ]
        }
    }


# JWT utility functions
def create_access_token(email: str) -> str:
    """Create a JWT access token without expiration."""
    payload = {
        "email": email,
        "iat": datetime.now(UTC),
    }
    token = jwt.encode(payload, settings.jwt_secret, algorithm="HS256")
    return token


class User2FA:
    TOKEN_DIGITS = 6
    SALT_LEN = 5
    TOKEN_VALID = timedelta(minutes=5)

    def __init__(self, user_enc_key: str):
        self.user_enc_key = user_enc_key

    def _enc(self, token: str) -> str:
        cipher = Fernet(self.user_enc_key)
        return cipher.encrypt(token.encode()).decode()

    def _dec(self, token: str) -> str:
        cipher = Fernet(self.user_enc_key)
        return cipher.decrypt(token).decode()

    def generate_code_token(self) -> tuple[str, str, datetime]:
        code = ''.join(random.SystemRandom().choice(string.digits) for _ in range(self.TOKEN_DIGITS))
        salt = ''.join(random.SystemRandom().choice(string.ascii_letters) for _ in range(self.SALT_LEN))

        valid_until = datetime.now() + self.TOKEN_VALID

        token = self._enc(f"{salt}#{code}#{valid_until.isoformat()}")

        return code, token, valid_until

    def verify_code_token(self, code: str, token: str) -> bool:
        if len(code) != self.TOKEN_DIGITS:
            return False
        if not all(map(lambda x: x.isdigit(), code)):
            return False

        try:
            raw_token = self._dec(token)
            salt, raw_code, raw_valid_until = raw_token.split('#')
            valid_until = datetime.fromisoformat(raw_valid_until)
        except Exception as e:
            # Invalid token format, decryption failed, or other parsing errors
            logger.warning(f"Failed to verify code token: {e}")
            return False

        if (valid_until - datetime.now()) < timedelta(0):
            return False

        return raw_code == code


auth_router = APIRouter(prefix="/api", tags=["auth"])


@auth_router.post(
    "/login/email",
    response_model=EmailAuthResponse,
    summary="Initiate email login",
    description="""
    Initiate the email-based login flow.

    This endpoint:
    1. Creates a new user if the email doesn't exist
    2. Generates a 6-digit verification code
    3. Sends the code to the provided email address
    4. Returns an encrypted token valid for 5 minutes

    The user must verify the code using the /login/email_verify endpoint.
    """,
    responses={
        200: {
            "description": "Login code sent successfully",
            "content": {
                "application/json": {
                    "example": {
                        "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                        "email_token_valid_until": "2025-12-31T12:05:00"
                    }
                }
            }
        },
        422: {
            "description": "Invalid email format"
        }
    }
)
async def login(login_data: EmailLoginRequest) -> EmailAuthResponse:
    """Initiate email login flow."""
    try:
        # Find user by username
        user = User.get(User.email == login_data.email)
    except User.DoesNotExist:
        user = User(email=login_data.email)
        user.save()


    # generate the code, token
    u2fa = User2FA(user.encrypt_key)
    code, token, valid_until = u2fa.generate_code_token()

    # Send code via email
    email_sent = send_login_code_email(login_data.email, code)
    if not email_sent:
        logger.warning(f"Failed to send email to {login_data.email}, but proceeding with login")

    logger.warning(f"Code to login for email: {login_data.email} is {code}.")

    return EmailAuthResponse(
        token=token,
        email_token_valid_until=valid_until,
    )



@auth_router.post(
    "/login/email_verify",
    response_model=AuthResponse,
    summary="Verify email login code",
    description="""
    Complete the email-based login flow by verifying the code.

    This endpoint:
    1. Validates the 6-digit code against the encrypted token
    2. Checks that the token hasn't expired (5-minute validity)
    3. Updates the user's last login timestamp
    4. Returns a JWT access token for authenticated requests

    The JWT token should be included in the Authorization header as:
    `Authorization: Bearer <access_token>`
    """,
    responses={
        200: {
            "description": "Login successful, JWT token returned",
            "content": {
                "application/json": {
                    "example": {
                        "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJlbWFpbCI6InVzZXJAZXhhbXBsZS5jb20iLCJpYXQiOjE3MDM5NjY0MDB9...",
                        "token_type": "bearer"
                    }
                }
            }
        },
        401: {
            "description": "Invalid code, expired token, or user not found"
        }
    }
)
async def verify_email_login(login_data: Email2LoginRequest) -> AuthResponse:
    """Verify email code and return JWT access token."""
    try:
        # Find user by username
        user = User.get(User.email == login_data.email)
    except User.DoesNotExist:
        raise HTTPException(status_code=401, detail="Invalid code.") from None

    # verify the code and token
    u2fa = User2FA(user.encrypt_key)
    if not u2fa.verify_code_token(login_data.email_code, login_data.token):
        raise HTTPException(status_code=401, detail="Invalid code.") from None

    token = create_access_token(login_data.email)

    user.last_login_at = datetime.now()
    user.save()

    return AuthResponse(
        access_token=token,
    )
