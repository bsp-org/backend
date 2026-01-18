"""Tests for email service."""

from src.email_service import parse_smtp_url


class TestParseSmtpUrl:
    """Test suite for parse_smtp_url function."""

    def test_parse_basic_smtp_url(self):
        """Test parsing basic SMTP URL without credentials."""
        result = parse_smtp_url("smtp://localhost:587")
        assert result.host == "localhost"
        assert result.port == 587
        assert result.username == ""
        assert result.password == ""
        assert result.use_tls is False

    def test_parse_smtps_url(self):
        """Test parsing SMTPS URL (secure)."""
        result = parse_smtp_url("smtps://mail.example.com:465")
        assert result.host == "mail.example.com"
        assert result.port == 465
        assert result.username == ""
        assert result.password == ""
        assert result.use_tls is True

    def test_parse_smtp_url_with_credentials(self):
        """Test parsing SMTP URL with username and password."""
        result = parse_smtp_url("smtp://user123:pass456@smtp.gmail.com:587")
        assert result.host == "smtp.gmail.com"
        assert result.port == 587
        assert result.username == "user123"
        assert result.password == "pass456"  # noqa: S105
        assert result.use_tls is False

    def test_parse_smtps_url_with_credentials(self):
        """Test parsing SMTPS URL with username and password."""
        result = parse_smtp_url("smtps://myuser:mypass@smtp.example.com:465")
        assert result.host == "smtp.example.com"
        assert result.port == 465
        assert result.username == "myuser"
        assert result.password == "mypass"  # noqa: S105
        assert result.use_tls is True

    def test_parse_smtp_url_default_port(self):
        """Test parsing SMTP URL without port uses default 587."""
        result = parse_smtp_url("smtp://smtp.example.com")
        assert result.host == "smtp.example.com"
        assert result.port == 587
        assert result.use_tls is False

    def test_parse_smtps_url_default_port(self):
        """Test parsing SMTPS URL without port uses default 465."""
        result = parse_smtp_url("smtps://smtp.example.com")
        assert result.host == "smtp.example.com"
        assert result.port == 465
        assert result.use_tls is True

    def test_parse_smtp_url_with_special_chars_in_password(self):
        """Test parsing SMTP URL with special characters in password."""
        result = parse_smtp_url("smtp://user:p@ss:w0rd!@smtp.example.com:587")
        assert result.host == "smtp.example.com"
        assert result.port == 587
        assert result.username == "user"
        assert result.password == "p@ss:w0rd!"  # noqa: S105
        assert result.use_tls is False

    def test_parse_smtp_url_with_username_only(self):
        """Test parsing SMTP URL with username but no password."""
        result = parse_smtp_url("smtp://user@smtp.example.com:587")
        assert result.host == "smtp.example.com"
        assert result.port == 587
        assert result.username == "user"
        assert result.password == ""
        assert result.use_tls is False

    def test_parse_smtp_url_custom_port(self):
        """Test parsing SMTP URL with custom port."""
        result = parse_smtp_url("smtp://smtp.example.com:2525")
        assert result.host == "smtp.example.com"
        assert result.port == 2525
        assert result.use_tls is False
