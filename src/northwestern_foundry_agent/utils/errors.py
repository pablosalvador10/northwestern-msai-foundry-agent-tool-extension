"""Custom exceptions for Northwestern Foundry Agent.

This module defines a hierarchy of custom exceptions for better error handling
and debugging throughout the application.
"""

from __future__ import annotations


class FoundryAgentError(Exception):
    """Base exception for all Foundry Agent errors.

    All custom exceptions in this package inherit from this base class,
    allowing for easy catching of all package-specific errors.

    Attributes:
        message: Human-readable error description.
        details: Optional additional context about the error.
    """

    def __init__(self, message: str, details: dict[str, object] | None = None) -> None:
        """Initialize the exception.

        Args:
            message: Human-readable error description.
            details: Optional dictionary with additional error context.
        """
        super().__init__(message)
        self.message = message
        self.details = details or {}

    def __str__(self) -> str:
        """Return string representation of the error."""
        if self.details:
            return f"{self.message} | Details: {self.details}"
        return self.message


class ConfigurationError(FoundryAgentError):
    """Raised when configuration is invalid or missing.

    This exception is raised when required configuration values are missing,
    malformed, or otherwise invalid.

    Example:
        >>> raise ConfigurationError(
        ...     "Missing Azure connection string",
        ...     details={"required_field": "AZURE_AI_PROJECT_CONNECTION_STRING"}
        ... )
    """


class ValidationError(FoundryAgentError):
    """Raised when input validation fails.

    This exception is raised when function arguments or data don't meet
    the required validation criteria.

    Example:
        >>> raise ValidationError(
        ...     "Invalid URL format",
        ...     details={"field": "endpoint", "value": "not-a-url"}
        ... )
    """


class FunctionInvocationError(FoundryAgentError):
    """Raised when Azure Function invocation fails.

    This exception is raised when calling an Azure Function results in
    an error, timeout, or unexpected response.

    Attributes:
        status_code: HTTP status code from the function response.
        function_name: Name of the Azure Function that failed.
    """

    def __init__(
        self,
        message: str,
        function_name: str | None = None,
        status_code: int | None = None,
        details: dict[str, object] | None = None,
    ) -> None:
        """Initialize the exception.

        Args:
            message: Human-readable error description.
            function_name: Name of the failed Azure Function.
            status_code: HTTP status code from the response.
            details: Optional dictionary with additional error context.
        """
        error_details = details or {}
        if function_name:
            error_details["function_name"] = function_name
        if status_code:
            error_details["status_code"] = status_code
        super().__init__(message, error_details)
        self.function_name = function_name
        self.status_code = status_code


class LogicAppError(FoundryAgentError):
    """Raised when Logic App invocation fails.

    This exception is raised when triggering a Logic App workflow results
    in an error, timeout, or unexpected response.

    Attributes:
        status_code: HTTP status code from the Logic App response.
        workflow_name: Name of the Logic App workflow that failed.
    """

    def __init__(
        self,
        message: str,
        workflow_name: str | None = None,
        status_code: int | None = None,
        details: dict[str, object] | None = None,
    ) -> None:
        """Initialize the exception.

        Args:
            message: Human-readable error description.
            workflow_name: Name of the failed Logic App workflow.
            status_code: HTTP status code from the response.
            details: Optional dictionary with additional error context.
        """
        error_details = details or {}
        if workflow_name:
            error_details["workflow_name"] = workflow_name
        if status_code:
            error_details["status_code"] = status_code
        super().__init__(message, error_details)
        self.workflow_name = workflow_name
        self.status_code = status_code


class ToolRegistrationError(FoundryAgentError):
    """Raised when tool registration with the agent fails.

    This exception is raised when attempting to register a tool
    (function or Logic App) with the Foundry agent fails.

    Example:
        >>> raise ToolRegistrationError(
        ...     "Failed to register tool",
        ...     details={"tool_name": "health_check", "reason": "Invalid schema"}
        ... )
    """
