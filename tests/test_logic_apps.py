"""Tests for Logic Apps integration client."""

from __future__ import annotations

import pytest

from northwestern_foundry_agent.integrations.logic_apps import (
    LogicAppRequest,
    LogicAppResponse,
    LogicAppsClient,
)
from northwestern_foundry_agent.integrations.logic_apps.models import WorkflowStatus
from northwestern_foundry_agent.utils.errors import ConfigurationError, LogicAppError


class TestLogicAppsClient:
    """Test cases for LogicAppsClient."""

    def test_client_initialization(self, test_settings):
        """Test client initializes with settings."""
        client = LogicAppsClient(settings=test_settings)

        assert client.trigger_url == "https://test-logic-app.azurewebsites.net/api/trigger"

    def test_client_initialization_with_overrides(self, test_settings):
        """Test client initializes with explicit parameters."""
        client = LogicAppsClient(
            settings=test_settings,
            trigger_url="https://custom-logic.azurewebsites.net/trigger",
            sas_token="custom-token",
        )

        assert client.trigger_url == "https://custom-logic.azurewebsites.net/trigger"
        assert client.sas_token == "custom-token"

    def test_client_missing_trigger_url(self):
        """Test client raises error when trigger URL is missing."""
        from northwestern_foundry_agent.config.settings import Settings

        settings = Settings(logic_app_trigger_url="")

        with pytest.raises(ConfigurationError) as exc_info:
            LogicAppsClient(settings=settings)

        assert "trigger URL is not configured" in str(exc_info.value)

    def test_get_headers_with_sas_token(self, test_settings):
        """Test headers include SAS token when provided."""
        client = LogicAppsClient(
            settings=test_settings,
            sas_token="test-sas-token",
        )
        headers = client._get_headers()

        assert headers["Content-Type"] == "application/json"
        assert headers["Authorization"] == "Bearer test-sas-token"

    def test_get_headers_without_sas_token(self, test_settings):
        """Test headers without SAS token."""
        client = LogicAppsClient(
            settings=test_settings,
            sas_token="",
        )
        headers = client._get_headers()

        assert "Authorization" not in headers

    @pytest.mark.asyncio
    async def test_trigger_success(self, test_settings, mock_logic_app_response, httpx_mock):
        """Test successful Logic App trigger."""
        httpx_mock.add_response(
            url="https://test-logic-app.azurewebsites.net/api/trigger",
            json=mock_logic_app_response,
        )

        client = LogicAppsClient(settings=test_settings)
        request = LogicAppRequest(
            action="test_action",
            input_data={"key": "value"},
        )

        response = await client.trigger(request)

        assert isinstance(response, LogicAppResponse)
        assert response.status == WorkflowStatus.SUCCEEDED
        assert response.is_successful is True
        assert response.workflow_run_id == "run-12345"

    @pytest.mark.asyncio
    async def test_trigger_error(self, test_settings, httpx_mock):
        """Test Logic App trigger with HTTP error."""
        # Need to add 3 responses for retry logic (3 attempts)
        for _ in range(3):
            httpx_mock.add_response(
                url="https://test-logic-app.azurewebsites.net/api/trigger",
                status_code=400,
                text="Bad Request",
            )

        client = LogicAppsClient(settings=test_settings)
        request = LogicAppRequest(action="test_action")

        with pytest.raises(LogicAppError) as exc_info:
            await client.trigger(request)

        assert exc_info.value.status_code == 400


class TestLogicAppRequest:
    """Test cases for LogicAppRequest model."""

    def test_default_values(self):
        """Test default values for request."""
        request = LogicAppRequest(action="test")

        assert request.action == "test"
        assert request.input_data == {}
        assert request.correlation_id is None
        assert request.metadata == {}

    def test_to_trigger_payload(self):
        """Test conversion to trigger payload."""
        request = LogicAppRequest(
            action="process",
            input_data={"document": "test.pdf"},
            correlation_id="corr-123",
            metadata={"source": "api"},
        )

        payload = request.to_trigger_payload()

        assert payload["action"] == "process"
        assert payload["inputData"] == {"document": "test.pdf"}
        assert payload["correlationId"] == "corr-123"
        assert payload["metadata"] == {"source": "api"}
        assert "timestamp" in payload


class TestLogicAppResponse:
    """Test cases for LogicAppResponse model."""

    def test_is_successful_true(self):
        """Test is_successful returns True for succeeded status."""
        response = LogicAppResponse(status=WorkflowStatus.SUCCEEDED)
        assert response.is_successful is True

    def test_is_successful_false(self):
        """Test is_successful returns False for failed status."""
        response = LogicAppResponse(status=WorkflowStatus.FAILED)
        assert response.is_successful is False

    def test_is_running_true(self):
        """Test is_running returns True for running status."""
        response = LogicAppResponse(status=WorkflowStatus.RUNNING)
        assert response.is_running is True

        response = LogicAppResponse(status=WorkflowStatus.PENDING)
        assert response.is_running is True

    def test_is_running_false(self):
        """Test is_running returns False for completed status."""
        response = LogicAppResponse(status=WorkflowStatus.SUCCEEDED)
        assert response.is_running is False

        response = LogicAppResponse(status=WorkflowStatus.FAILED)
        assert response.is_running is False


class TestWorkflowStatus:
    """Test cases for WorkflowStatus enum."""

    def test_status_values(self):
        """Test all status values exist."""
        assert WorkflowStatus.PENDING.value == "pending"
        assert WorkflowStatus.RUNNING.value == "running"
        assert WorkflowStatus.SUCCEEDED.value == "succeeded"
        assert WorkflowStatus.FAILED.value == "failed"
        assert WorkflowStatus.CANCELLED.value == "cancelled"
