"""Tests for Azure Functions integration client."""

from __future__ import annotations

import pytest

from northwestern_foundry_agent.integrations.azure_functions import (
    AzureFunctionsClient,
    HealthCheckResponse,
    QuoteResponse,
)
from northwestern_foundry_agent.utils.errors import (
    ConfigurationError,
    FunctionInvocationError,
)


class TestAzureFunctionsClient:
    """Test cases for AzureFunctionsClient."""

    def test_client_initialization(self, test_settings):
        """Test client initializes with settings."""
        client = AzureFunctionsClient(settings=test_settings)

        assert client.base_url == "https://test-functions.azurewebsites.net"
        assert client.function_key == "test-function-key"

    def test_client_initialization_with_overrides(self, test_settings):
        """Test client initializes with explicit parameters."""
        client = AzureFunctionsClient(
            settings=test_settings,
            base_url="https://custom.azurewebsites.net",
            function_key="custom-key",
        )

        assert client.base_url == "https://custom.azurewebsites.net"
        assert client.function_key == "custom-key"

    def test_client_missing_base_url(self):
        """Test client raises error when base URL is missing."""
        from northwestern_foundry_agent.config.settings import Settings

        settings = Settings(azure_function_app_url="")

        with pytest.raises(ConfigurationError) as exc_info:
            AzureFunctionsClient(settings=settings)

        assert "base URL is not configured" in str(exc_info.value)

    def test_client_strips_trailing_slash(self, test_settings):
        """Test client strips trailing slash from base URL."""
        client = AzureFunctionsClient(
            settings=test_settings,
            base_url="https://test.azurewebsites.net/",
        )

        assert client.base_url == "https://test.azurewebsites.net"

    def test_get_headers_with_function_key(self, test_settings):
        """Test headers include function key."""
        client = AzureFunctionsClient(settings=test_settings)
        headers = client._get_headers()

        assert headers["Content-Type"] == "application/json"
        assert headers["Accept"] == "application/json"
        assert headers["x-functions-key"] == "test-function-key"

    def test_get_headers_without_function_key(self):
        """Test headers without function key."""
        # Create client with explicitly empty function_key
        from northwestern_foundry_agent.config.settings import Settings

        custom_settings = Settings(
            azure_function_app_url="https://test-functions.azurewebsites.net",
            azure_function_key="",
        )
        client = AzureFunctionsClient(settings=custom_settings)
        headers = client._get_headers()

        assert "x-functions-key" not in headers

    @pytest.mark.asyncio
    async def test_health_check_success(self, test_settings, mock_health_response, httpx_mock):
        """Test successful health check call."""
        httpx_mock.add_response(
            url="https://test-functions.azurewebsites.net/api/health",
            json=mock_health_response,
        )

        client = AzureFunctionsClient(settings=test_settings)
        response = await client.health_check()

        assert isinstance(response, HealthCheckResponse)
        assert response.status == "healthy"
        assert response.is_healthy is True
        assert response.service_name == "northwestern-foundry-functions"

    @pytest.mark.asyncio
    async def test_health_check_error(self, test_settings, httpx_mock):
        """Test health check with HTTP error."""
        # Need to add 3 responses for retry logic (3 attempts)
        for _ in range(3):
            httpx_mock.add_response(
                url="https://test-functions.azurewebsites.net/api/health",
                status_code=500,
                text="Internal Server Error",
            )

        client = AzureFunctionsClient(settings=test_settings)

        with pytest.raises(FunctionInvocationError) as exc_info:
            await client.health_check()

        assert exc_info.value.status_code == 500

    @pytest.mark.asyncio
    async def test_quote_of_the_day_success(self, test_settings, mock_quote_response, httpx_mock):
        """Test successful quote retrieval."""
        httpx_mock.add_response(
            url="https://test-functions.azurewebsites.net/api/quote?category=motivation",
            json=mock_quote_response,
        )

        client = AzureFunctionsClient(settings=test_settings)
        response = await client.quote_of_the_day(category="motivation")

        assert isinstance(response, QuoteResponse)
        assert response.quote == "The only way to do great work is to love what you do."
        assert response.author == "Steve Jobs"
        assert response.category == "motivation"

    @pytest.mark.asyncio
    async def test_quote_of_the_day_with_category(self, test_settings, httpx_mock):
        """Test quote retrieval with different category."""
        mock_response = {
            "quote": "Test wisdom quote",
            "author": "Test Author",
            "category": "wisdom",
            "timestamp": "2024-01-15T10:30:00.000000+00:00",
        }
        httpx_mock.add_response(
            url="https://test-functions.azurewebsites.net/api/quote?category=wisdom",
            json=mock_response,
        )

        client = AzureFunctionsClient(settings=test_settings)
        response = await client.quote_of_the_day(category="wisdom")

        assert response.category == "wisdom"


class TestHealthCheckResponse:
    """Test cases for HealthCheckResponse model."""

    def test_is_healthy_true(self):
        """Test is_healthy returns True for healthy status."""
        response = HealthCheckResponse(status="healthy")
        assert response.is_healthy is True

    def test_is_healthy_false(self):
        """Test is_healthy returns False for unhealthy status."""
        response = HealthCheckResponse(status="unhealthy")
        assert response.is_healthy is False

    def test_is_healthy_case_insensitive(self):
        """Test is_healthy is case insensitive."""
        response = HealthCheckResponse(status="HEALTHY")
        assert response.is_healthy is True


class TestQuoteResponse:
    """Test cases for QuoteResponse model."""

    def test_default_category(self):
        """Test default category is motivation."""
        response = QuoteResponse(
            quote="Test quote",
            author="Test Author",
        )
        assert response.category == "motivation"

    def test_custom_category(self):
        """Test custom category."""
        response = QuoteResponse(
            quote="Test quote",
            author="Test Author",
            category="wisdom",
        )
        assert response.category == "wisdom"
