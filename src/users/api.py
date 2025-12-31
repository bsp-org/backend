"""Authentication API endpoints."""

import base64
import logging
import random
import string
from datetime import UTC, datetime, timedelta

import jwt
from Crypto.Cipher import AES
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, EmailStr

from src.config import settings
from src.users.models import User

logger = logging.getLogger(__name__)


class EmailLoginRequest(BaseModel):
    """Request model for user registration."""

    email: EmailStr


class Email2LoginRequest(BaseModel):
    """Request model for user registration."""

    email: EmailStr
    email_code: str
    token: str


class EmailAuthResponse(BaseModel):
    """The response for /login/email endpoint."""
    token: str
    email_token_valid_until: datetime


class AuthResponse(BaseModel):
    """Response model for authentication endpoints."""

    access_token: str
    token_type: str = "bearer"
    token_valid_until: datetime | None = None


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
    TOKEN_VALID = timedelta(minutes=5)
    IV = b'OurBSP_IV4567890'

    def __init__(self, user_enc_key: str):
        # Decode the base64-encoded key to get the 32-byte AES key
        self.user_enc_key = base64.b64decode(user_enc_key)

    def _enc(self, token: str) -> str:
        cipher = AES.new(self.user_enc_key, AES.MODE_CFB, self.IV)
        return base64.b64encode(cipher.encrypt(token.encode())).decode()

    def _dec(self, token: str) -> str:
        cipher = AES.new(self.user_enc_key, AES.MODE_CFB, self.IV)
        return cipher.decrypt(base64.b64decode(token)).decode()

    def generate_code_token(self) -> tuple[str, str, datetime]:
        code = ''.join(random.SystemRandom().choice(string.digits) for _ in range(self.TOKEN_DIGITS))

        valid_until = datetime.now() + self.TOKEN_VALID

        token = self._enc(f"{code}#{valid_until.isoformat()}")

        return code, token, valid_until

    def verify_code_token(self, code: str, token: str) -> bool:
        if len(code) != self.TOKEN_DIGITS:
            return False
        if not all(map(lambda x: x.isdigit(), code)):
            return False

        try:
            raw_token = self._dec(token)
            raw_code, raw_valid_until = raw_token.split('#')
            valid_until = datetime.fromisoformat(raw_valid_until)
        except Exception as e:
            # Invalid token format, decryption failed, or other parsing errors
            logger.warning(f"Failed to verify code token: {e}")
            return False

        if (valid_until - datetime.now()) < timedelta(0):
            return False

        return raw_code == code


auth_router = APIRouter(prefix="/api", tags=["auth"])


@auth_router.post("/login/email", response_model=EmailAuthResponse)
async def login(request: EmailLoginRequest) -> EmailAuthResponse:
    """Login a user and return a JWT token."""
    try:
        # Find user by username
        user = User.get(User.email == request.email)
    except User.DoesNotExist:
        user = User(email=request.email)
        user.save()


    # generate the code, token
    u2fa = User2FA(user.encrypt_key)
    code, token, valid_until = u2fa.generate_code_token()

    # TODO: send code via email
    print(f"Code to login for email: {request.email} is {code}.")

    return EmailAuthResponse(
        token=token,
        email_token_valid_until=valid_until,
    )



@auth_router.post("/login/email_verify", response_model=AuthResponse)
async def verify_email_login(request: Email2LoginRequest) -> AuthResponse:
    """Verify email code and return a JWT token."""
    try:
        # Find user by username
        user = User.get(User.email == request.email)
    except User.DoesNotExist:
        raise HTTPException(status_code=401, detail="Invalid code.") from None

    # verify the code and token
    u2fa = User2FA(user.encrypt_key)
    if not u2fa.verify_code_token(request.email_code, request.token):
        raise HTTPException(status_code=401, detail="Invalid code.") from None

    token = create_access_token(request.email)

    user.last_login_at = datetime.now()
    user.save()

    return AuthResponse(
        access_token=token,
    )
