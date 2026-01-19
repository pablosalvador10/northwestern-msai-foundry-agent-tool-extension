"""Tests for utility modules."""

from __future__ import annotations

import pytest

from northwestern_foundry_agent.utils.errors import (
    ConfigurationError,
    FoundryAgentError,
    FunctionInvocationError,
    LogicAppError,
    ToolRegistrationError,
    ValidationError,
)
from northwestern_foundry_agent.utils.validation import (
    validate_in_list,
    validate_not_empty,
    validate_positive_int,
    validate_url,
)


class TestErrors:
    """Test cases for custom exceptions."""

    def test_foundry_agent_error_basic(self):
        """Test basic FoundryAgentError."""
        error = FoundryAgentError("Test error")

        assert str(error) == "Test error"
        assert error.message == "Test error"
        assert error.details == {}

    def test_foundry_agent_error_with_details(self):
        """Test FoundryAgentError with details."""
        error = FoundryAgentError(
            "Test error",
            details={"key": "value", "count": 42},
        )

        assert "Test error" in str(error)
        assert "Details" in str(error)
        assert error.details == {"key": "value", "count": 42}

    def test_configuration_error(self):
        """Test ConfigurationError inherits from FoundryAgentError."""
        error = ConfigurationError("Config missing")

        assert isinstance(error, FoundryAgentError)
        assert error.message == "Config missing"

    def test_validation_error(self):
        """Test ValidationError with field details."""
        error = ValidationError(
            "Invalid input",
            details={"field": "email", "value": "not-an-email"},
        )

        assert isinstance(error, FoundryAgentError)
        assert error.details["field"] == "email"

    def test_function_invocation_error(self):
        """Test FunctionInvocationError with status code."""
        error = FunctionInvocationError(
            "Function failed",
            function_name="health_check",
            status_code=500,
        )

        assert isinstance(error, FoundryAgentError)
        assert error.function_name == "health_check"
        assert error.status_code == 500
        assert "health_check" in str(error)

    def test_logic_app_error(self):
        """Test LogicAppError with workflow info."""
        error = LogicAppError(
            "Workflow failed",
            workflow_name="process_request",
            status_code=400,
        )

        assert isinstance(error, FoundryAgentError)
        assert error.workflow_name == "process_request"
        assert error.status_code == 400

    def test_tool_registration_error(self):
        """Test ToolRegistrationError."""
        error = ToolRegistrationError(
            "Failed to register tool",
            details={"tool_name": "my_tool"},
        )

        assert isinstance(error, FoundryAgentError)
        assert error.details["tool_name"] == "my_tool"


class TestValidation:
    """Test cases for validation utilities."""

    def test_validate_not_empty_success(self):
        """Test validate_not_empty with valid input."""
        result = validate_not_empty("  hello  ", "name")
        assert result == "hello"

    def test_validate_not_empty_failure(self):
        """Test validate_not_empty with empty input."""
        with pytest.raises(ValidationError) as exc_info:
            validate_not_empty("   ", "name")

        assert "name" in str(exc_info.value)
        assert "cannot be empty" in str(exc_info.value)

    def test_validate_not_empty_no_strip(self):
        """Test validate_not_empty without stripping."""
        result = validate_not_empty("  hello  ", "name", strip_whitespace=False)
        assert result == "  hello  "

    def test_validate_url_success(self):
        """Test validate_url with valid URLs."""
        assert validate_url("https://example.com") == "https://example.com"
        assert validate_url("http://localhost:8080/api") == "http://localhost:8080/api"
        assert validate_url("https://api.example.com/v1/data") == "https://api.example.com/v1/data"

    def test_validate_url_empty(self):
        """Test validate_url with empty input."""
        with pytest.raises(ValidationError) as exc_info:
            validate_url("")

        assert "cannot be empty" in str(exc_info.value)

    def test_validate_url_invalid(self):
        """Test validate_url with invalid URL."""
        with pytest.raises(ValidationError) as exc_info:
            validate_url("not-a-url")

        assert "not a valid URL" in str(exc_info.value)

    def test_validate_url_require_https(self):
        """Test validate_url with HTTPS requirement."""
        # HTTPS should pass
        assert validate_url("https://example.com", require_https=True) == "https://example.com"

        # HTTP should fail
        with pytest.raises(ValidationError) as exc_info:
            validate_url("http://example.com", require_https=True)

        assert "must use HTTPS" in str(exc_info.value)

    def test_validate_positive_int_success(self):
        """Test validate_positive_int with valid input."""
        assert validate_positive_int(5, "count") == 5
        assert validate_positive_int(1, "count", min_value=1) == 1
        assert validate_positive_int(50, "count", min_value=1, max_value=100) == 50

    def test_validate_positive_int_below_min(self):
        """Test validate_positive_int below minimum."""
        with pytest.raises(ValidationError) as exc_info:
            validate_positive_int(0, "count", min_value=1)

        assert "at least 1" in str(exc_info.value)

    def test_validate_positive_int_above_max(self):
        """Test validate_positive_int above maximum."""
        with pytest.raises(ValidationError) as exc_info:
            validate_positive_int(150, "count", max_value=100)

        assert "at most 100" in str(exc_info.value)

    def test_validate_in_list_success(self):
        """Test validate_in_list with valid value."""
        result = validate_in_list("active", ["active", "inactive"], "status")
        assert result == "active"

    def test_validate_in_list_failure(self):
        """Test validate_in_list with invalid value."""
        with pytest.raises(ValidationError) as exc_info:
            validate_in_list("unknown", ["active", "inactive"], "status")

        assert "must be one of" in str(exc_info.value)
