"""Tests for login endpoints."""

from unittest.mock import patch

import jwt
import pytest

from src.config import settings
from src.users.models import User


class TestLoginEmail:
    """Test suite for /api/login/email endpoint."""

    @pytest.mark.asyncio
    @patch("src.users.api.send_login_code_email")
    async def test_login_email_new_user(self, mock_send_email, client):
        """Test login with a new user creates account and sends email."""
        mock_send_email.return_value = True

        response = await client.post("/api/login/email", json={"email": "newuser@example.com"})

        assert response.status_code == 200
        data = response.json()
        assert "token" in data
        assert "email_token_valid_until" in data

        # Verify email was sent
        mock_send_email.assert_called_once()
        call_args = mock_send_email.call_args
        assert call_args[0][0] == "newuser@example.com"
        assert len(call_args[0][1]) == 6  # Code should be 6 digits
        assert call_args[0][1].isdigit()

        # Verify user was created
        user = User.get(User.email == "newuser@example.com")
        assert user is not None
        assert user.email == "newuser@example.com"

    @pytest.mark.asyncio
    @patch("src.users.api.send_login_code_email")
    async def test_login_email_existing_user(self, mock_send_email, client):
        """Test login with an existing user sends email."""
        mock_send_email.return_value = True

        # Create existing user
        user = User(email="existing@example.com")
        user.save()

        response = await client.post("/api/login/email", json={"email": "existing@example.com"})

        assert response.status_code == 200
        data = response.json()
        assert "token" in data
        assert "email_token_valid_until" in data

        # Verify email was sent
        mock_send_email.assert_called_once()
        call_args = mock_send_email.call_args
        assert call_args[0][0] == "existing@example.com"

        # Verify only one user exists
        assert User.select().where(User.email == "existing@example.com").count() == 1

    @pytest.mark.asyncio
    @patch("src.users.api.send_login_code_email")
    async def test_login_email_invalid_email(self, mock_send_email, client):
        """Test login with invalid email format."""
        response = await client.post("/api/login/email", json={"email": "not-an-email"})

        assert response.status_code == 422  # Validation error
        mock_send_email.assert_not_called()

    @pytest.mark.asyncio
    @patch("src.users.api.send_login_code_email")
    async def test_login_email_continues_on_email_failure(self, mock_send_email, client):
        """Test login continues even if email sending fails."""
        mock_send_email.return_value = False

        response = await client.post("/api/login/email", json={"email": "test@example.com"})

        # Should still return success even if email fails
        assert response.status_code == 200
        data = response.json()
        assert "token" in data
        assert "email_token_valid_until" in data

        mock_send_email.assert_called_once()


class TestLoginEmailVerify:
    """Test suite for /api/login/email_verify endpoint."""

    @pytest.mark.asyncio
    @patch("src.users.api.send_login_code_email")
    async def test_verify_email_login_success(self, mock_send_email, client):
        """Test successful email verification."""
        mock_send_email.return_value = True

        # First, get a login code
        login_response = await client.post("/api/login/email", json={"email": "verify@example.com"})
        assert login_response.status_code == 200
        login_data = login_response.json()

        # Extract the code from the mock call
        code = mock_send_email.call_args[0][1]

        # Now verify with the code
        verify_response = await client.post(
            "/api/login/email_verify",
            json={"email": "verify@example.com", "email_code": code, "token": login_data["token"]},
        )

        assert verify_response.status_code == 200
        verify_data = verify_response.json()
        assert "access_token" in verify_data
        assert verify_data["token_type"] == "bearer"  # noqa: S105

        # Verify the JWT token
        decoded = jwt.decode(verify_data["access_token"], settings.jwt_secret, algorithms=["HS256"])
        assert decoded["email"] == "verify@example.com"
        assert "iat" in decoded

        # Verify user's last_login_at was updated
        user = User.get(User.email == "verify@example.com")
        assert user.last_login_at is not None

    @pytest.mark.asyncio
    @patch("src.users.api.send_login_code_email")
    async def test_verify_email_login_wrong_code(self, mock_send_email, client):
        """Test verification with wrong code."""
        mock_send_email.return_value = True

        # First, get a login code
        login_response = await client.post(
            "/api/login/email", json={"email": "wrongcode@example.com"}
        )
        login_data = login_response.json()

        # Verify with wrong code
        verify_response = await client.post(
            "/api/login/email_verify",
            json={
                "email": "wrongcode@example.com",
                "email_code": "000000",  # Wrong code
                "token": login_data["token"],
            },
        )

        assert verify_response.status_code == 401
        assert verify_response.json()["detail"] == "Invalid code."

    @pytest.mark.asyncio
    @patch("src.users.api.send_login_code_email")
    async def test_verify_email_login_nonexistent_user(self, mock_send_email, client):
        """Test verification for a user that doesn't exist."""
        verify_response = await client.post(
            "/api/login/email_verify",
            json={
                "email": "nonexistent@example.com",
                "email_code": "123456",
                "token": "some-token",
            },
        )

        assert verify_response.status_code == 401
        assert verify_response.json()["detail"] == "Invalid code."

    @pytest.mark.asyncio
    @patch("src.users.api.send_login_code_email")
    async def test_verify_email_login_invalid_token(self, mock_send_email, client):
        """Test verification with invalid token."""
        mock_send_email.return_value = True

        # First, get a login code
        login_response = await client.post(
            "/api/login/email", json={"email": "invalidtoken@example.com"}
        )
        assert login_response.status_code == 200

        # Extract the code from the mock call
        code = mock_send_email.call_args[0][1]

        # Verify with invalid token
        verify_response = await client.post(
            "/api/login/email_verify",
            json={
                "email": "invalidtoken@example.com",
                "email_code": code,
                "token": "invalid-token-format",
            },
        )

        assert verify_response.status_code == 401
        assert verify_response.json()["detail"] == "Invalid code."

    @pytest.mark.asyncio
    @patch("src.users.api.send_login_code_email")
    async def test_verify_email_login_wrong_email(self, mock_send_email, client):
        """Test verification with wrong email address."""
        mock_send_email.return_value = True

        # First, get a login code for one email
        login_response = await client.post(
            "/api/login/email", json={"email": "correct@example.com"}
        )
        login_data = login_response.json()
        code = mock_send_email.call_args[0][1]

        # Try to verify with a different email
        verify_response = await client.post(
            "/api/login/email_verify",
            json={"email": "wrong@example.com", "email_code": code, "token": login_data["token"]},
        )

        assert verify_response.status_code == 401
        assert verify_response.json()["detail"] == "Invalid code."

    @pytest.mark.asyncio
    @patch("src.users.api.send_login_code_email")
    async def test_verify_email_login_code_format_validation(self, mock_send_email, client):
        """Test verification with invalid code format."""
        mock_send_email.return_value = True

        # First, get a login code
        login_response = await client.post("/api/login/email", json={"email": "format@example.com"})
        login_data = login_response.json()

        # Test with wrong length
        verify_response = await client.post(
            "/api/login/email_verify",
            json={
                "email": "format@example.com",
                "email_code": "12345",  # Too short
                "token": login_data["token"],
            },
        )
        assert verify_response.status_code == 401

        # Test with non-digits
        verify_response = await client.post(
            "/api/login/email_verify",
            json={
                "email": "format@example.com",
                "email_code": "12345a",
                "token": login_data["token"],
            },
        )
        assert verify_response.status_code == 401
