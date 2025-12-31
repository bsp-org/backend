"""Tests for OpenAPI schema."""

import pytest


@pytest.mark.asyncio
async def test_openapi_schema_generation(client):
    """Test that OpenAPI schema is generated correctly."""
    response = await client.get("/openapi.json")
    assert response.status_code == 200

    schema = response.json()

    # Check basic schema info
    assert schema["info"]["title"] == "Bible Search API"
    assert schema["info"]["version"] == "0.0.0"
    assert "description" in schema["info"]
    assert schema["info"]["contact"]["email"] == "biblesearchproject@gmail.com"
    assert schema["info"]["license"]["name"] == "MIT"


@pytest.mark.asyncio
async def test_openapi_auth_endpoints(client):
    """Test that authentication endpoints are documented."""
    response = await client.get("/openapi.json")
    schema = response.json()

    # Check that login endpoints exist
    assert "/api/login/email" in schema["paths"]
    assert "/api/login/email_verify" in schema["paths"]

    # Check login/email endpoint
    login_endpoint = schema["paths"]["/api/login/email"]["post"]
    assert login_endpoint["summary"] == "Initiate email login"
    assert "description" in login_endpoint
    assert "auth" in login_endpoint["tags"]

    # Check request body schema
    assert "requestBody" in login_endpoint
    request_schema = login_endpoint["requestBody"]["content"]["application/json"]["schema"]
    assert "$ref" in request_schema

    # Check responses
    assert "200" in login_endpoint["responses"]
    assert "422" in login_endpoint["responses"]

    # Check login/email_verify endpoint
    verify_endpoint = schema["paths"]["/api/login/email_verify"]["post"]
    assert verify_endpoint["summary"] == "Verify email login code"
    assert "description" in verify_endpoint
    assert "auth" in verify_endpoint["tags"]

    # Check responses
    assert "200" in verify_endpoint["responses"]
    assert "401" in verify_endpoint["responses"]


@pytest.mark.asyncio
async def test_openapi_schema_models(client):
    """Test that Pydantic models have examples."""
    response = await client.get("/openapi.json")
    schema = response.json()

    components = schema["components"]["schemas"]

    # Check EmailLoginRequest
    assert "EmailLoginRequest" in components
    email_login = components["EmailLoginRequest"]
    assert "examples" in email_login
    assert len(email_login["examples"]) > 0

    # Check Email2LoginRequest
    assert "Email2LoginRequest" in components
    email2_login = components["Email2LoginRequest"]
    assert "examples" in email2_login

    # Check EmailAuthResponse
    assert "EmailAuthResponse" in components
    email_auth_resp = components["EmailAuthResponse"]
    assert "examples" in email_auth_resp

    # Check AuthResponse
    assert "AuthResponse" in components
    auth_resp = components["AuthResponse"]
    assert "examples" in auth_resp


@pytest.mark.asyncio
async def test_docs_ui_accessible(client):
    """Test that Swagger UI docs are accessible."""
    response = await client.get("/docs")
    assert response.status_code == 200
    assert b"swagger" in response.content.lower()


@pytest.mark.asyncio
async def test_redoc_ui_accessible(client):
    """Test that ReDoc UI is accessible."""
    response = await client.get("/redoc")
    assert response.status_code == 200
    assert b"redoc" in response.content.lower()
