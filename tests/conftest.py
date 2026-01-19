"""Pytest configuration and fixtures."""

from __future__ import annotations

import pytest

from northwestern_foundry_agent.config.settings import Settings


@pytest.fixture
def test_settings() -> Settings:
    """Create test settings with mock values."""
    return Settings(
        azure_ai_project_connection_string="test-connection-string",
        azure_subscription_id="test-subscription-id",
        azure_resource_group="test-resource-group",
        azure_ai_project_name="test-project",
        azure_openai_endpoint="https://test.openai.azure.com/",
        azure_openai_deployment="gpt-4o",
        azure_function_app_url="https://test-functions.azurewebsites.net",
        azure_function_key="test-function-key",
        logic_app_trigger_url="https://test-logic-app.azurewebsites.net/api/trigger",
        log_level="DEBUG",
        log_format="text",
        debug=True,
    )


@pytest.fixture
def mock_health_response() -> dict:
    """Mock response for health check endpoint."""
    return {
        "status": "healthy",
        "service_name": "northwestern-foundry-functions",
        "version": "1.0.0",
        "timestamp": "2024-01-15T10:30:00.000000+00:00",
        "details": {
            "python_version": "3.11.0",
            "function_app": "running",
        },
    }


@pytest.fixture
def mock_quote_response() -> dict:
    """Mock response for quote endpoint."""
    return {
        "quote": "The only way to do great work is to love what you do.",
        "author": "Steve Jobs",
        "category": "motivation",
        "timestamp": "2024-01-15T10:30:00.000000+00:00",
    }


@pytest.fixture
def mock_logic_app_response() -> dict:
    """Mock response for Logic App trigger."""
    return {
        "workflow_run_id": "run-12345",
        "status": "succeeded",
        "output_data": {"result": "processed"},
        "error": None,
        "started_at": "2024-01-15T10:30:00.000000+00:00",
        "completed_at": "2024-01-15T10:30:05.000000+00:00",
    }
