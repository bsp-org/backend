"""Unit tests for User2FA class."""

import base64
from datetime import datetime, timedelta
from unittest.mock import patch

import pytest

from src.users.api import User2FA
from src.users.models import generate_encrypt_key


class TestUser2FA:
    """Test suite for User2FA class."""

    @pytest.fixture
    def encryption_key(self) -> str:
        """Provide a valid 32-byte encryption key for AES-256, base64-encoded."""
        # Generate a 32-byte key and base64-encode it (as stored in the database)
        return generate_encrypt_key()

    @pytest.fixture
    def user_2fa(self, encryption_key):
        """Create a User2FA instance for testing."""
        return User2FA(encryption_key)

    def test_init(self, encryption_key):
        """Test User2FA initialization."""
        user_2fa = User2FA(encryption_key)
        assert user_2fa is not None
        assert hasattr(user_2fa, "user_enc_key")
        # user_enc_key should be the decoded bytes (32 bytes for AES-256)
        assert user_2fa.user_enc_key == encryption_key
        assert len(base64.b64decode(user_2fa.user_enc_key)) == 32

    def test_encryption_decryption_roundtrip(self, user_2fa):
        """Test that encryption and decryption are inverse operations."""
        original_text = "test_token_123"
        encrypted = user_2fa._enc(original_text)
        decrypted = user_2fa._dec(encrypted)
        assert decrypted == original_text

    def test_encryption_produces_different_output(self, user_2fa):
        """Test that encryption produces different output than input."""
        original_text = "test_token"
        encrypted = user_2fa._enc(original_text)
        assert encrypted != original_text

    def test_generate_code_token_returns_tuple(self, user_2fa):
        """Test that generate_code_token returns a tuple of (code, token, valid_until)."""
        result = user_2fa.generate_code_token()
        assert isinstance(result, tuple)
        assert len(result) == 3
        code, token, valid_until = result
        assert isinstance(code, str)
        assert isinstance(token, str)
        assert isinstance(valid_until, datetime)

    def test_generate_code_has_correct_length(self, user_2fa):
        """Test that generated code has TOKEN_DIGITS length."""
        code, _, _ = user_2fa.generate_code_token()
        assert len(code) == User2FA.TOKEN_DIGITS

    def test_generate_code_contains_only_digits(self, user_2fa):
        """Test that generated code contains only digits."""
        code, _, _ = user_2fa.generate_code_token()
        assert code.isdigit()

    def test_generate_code_validity_period(self, user_2fa):
        """Test that the validity period is set correctly."""
        before = datetime.now()
        _, _, valid_until = user_2fa.generate_code_token()
        after = datetime.now()

        expected_min = before + User2FA.TOKEN_VALID
        expected_max = after + User2FA.TOKEN_VALID

        assert expected_min <= valid_until <= expected_max

    def test_generate_code_produces_unique_codes(self, user_2fa):
        """Test that multiple calls produce different codes."""
        codes = [user_2fa.generate_code_token()[0] for _ in range(10)]
        # While theoretically possible to get duplicates with random generation,
        # it's extremely unlikely with 6-digit codes
        assert len(set(codes)) > 1

    def test_verify_code_token_valid_code(self, user_2fa):
        """Test verification with valid code and token."""
        code, token, _ = user_2fa.generate_code_token()
        assert user_2fa.verify_code_token(code, token) is True

    def test_verify_code_token_invalid_code_wrong_digits(self, user_2fa):
        """Test verification with wrong code."""
        code, token, _ = user_2fa.generate_code_token()
        wrong_code = "000000" if code != "000000" else "111111"
        assert user_2fa.verify_code_token(wrong_code, token) is False

    def test_verify_code_token_invalid_code_wrong_length(self, user_2fa):
        """Test verification with code of wrong length."""
        _, token, _ = user_2fa.generate_code_token()
        assert user_2fa.verify_code_token("12345", token) is False
        assert user_2fa.verify_code_token("1234567", token) is False

    def test_verify_code_token_invalid_code_non_digits(self, user_2fa):
        """Test verification with code containing non-digits."""
        _, token, _ = user_2fa.generate_code_token()
        assert user_2fa.verify_code_token("12345a", token) is False
        assert user_2fa.verify_code_token("abcdef", token) is False

    @patch("src.users.api.datetime")
    def test_verify_code_token_expired(self, mock_datetime, user_2fa):
        """Test verification with expired token."""
        # Generate a code/token
        now = datetime(2025, 1, 1, 12, 0, 0)
        mock_datetime.now.return_value = now
        mock_datetime.fromisoformat = datetime.fromisoformat

        code, token, _ = user_2fa.generate_code_token()

        # Move time forward beyond TOKEN_VALID period
        future_time = now + User2FA.TOKEN_VALID + timedelta(seconds=1)
        mock_datetime.now.return_value = future_time

        assert user_2fa.verify_code_token(code, token) is False

    def test_verify_code_token_just_before_expiry(self, user_2fa):
        """Test verification just before token expires."""
        code, token, _ = user_2fa.generate_code_token()
        # Should still be valid immediately after generation
        assert user_2fa.verify_code_token(code, token) is True

    def test_verify_code_token_empty_code(self, user_2fa):
        """Test verification with empty code."""
        _, token, _ = user_2fa.generate_code_token()
        assert user_2fa.verify_code_token("", token) is False

    def test_multiple_instances_with_same_key(self, encryption_key):
        """Test that multiple instances with same key can decrypt each other's tokens."""
        user_2fa_1 = User2FA(encryption_key)
        user_2fa_2 = User2FA(encryption_key)

        code, token, _ = user_2fa_1.generate_code_token()
        assert user_2fa_2.verify_code_token(code, token) is True

    def test_multiple_instances_with_different_keys(self):
        """Test that instances with different keys cannot decrypt each other's tokens."""
        # Create two different 32-byte keys, base64-encoded
        key1 = base64.b64encode(b"Key1Key1Key1Key1Key1Key1Key1Key1").decode("utf-8")
        key2 = base64.b64encode(b"Key2Key2Key2Key2Key2Key2Key2Key2").decode("utf-8")

        user_2fa_1 = User2FA(key1)
        user_2fa_2 = User2FA(key2)

        code, token, _ = user_2fa_1.generate_code_token()
        # Should return False because decryption with wrong key produces garbage
        assert user_2fa_2.verify_code_token(code, token) is False

    def test_verify_code_token_invalid_base64(self, user_2fa):
        """Test verification with invalid base64 token."""
        assert user_2fa.verify_code_token("123456", "not-valid-base64!@#") is False

    def test_verify_code_token_malformed_token_no_separator(self, user_2fa):
        """Test verification with token that doesn't contain '#' separator."""
        # Create a valid encrypted token but without the '#' separator
        malformed = user_2fa._enc("123456")
        assert user_2fa.verify_code_token("123456", malformed) is False

    def test_verify_code_token_invalid_datetime_format(self, user_2fa):
        """Test verification with token containing invalid datetime."""
        malformed = user_2fa._enc("123456#not-a-datetime")
        assert user_2fa.verify_code_token("123456", malformed) is False

    def test_token_constants(self):
        """Test that class constants have expected values."""
        assert User2FA.TOKEN_DIGITS == 6
        assert User2FA.TOKEN_VALID == timedelta(minutes=5)
