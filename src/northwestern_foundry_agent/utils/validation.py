"""Input validation utilities for Northwestern Foundry Agent.

This module provides validation functions for common input patterns
used throughout the application.
"""

from __future__ import annotations

import re
from typing import TypeVar

from northwestern_foundry_agent.utils.errors import ValidationError

T = TypeVar("T")

# URL validation pattern
URL_PATTERN = re.compile(
    r"^https?://"  # http:// or https://
    r"(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|"  # domain
    r"localhost|"  # localhost
    r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})"  # or IP
    r"(?::\d+)?"  # optional port
    r"(?:/?|[/?]\S+)$",
    re.IGNORECASE,
)


def validate_not_empty(
    value: str,
    field_name: str,
    strip_whitespace: bool = True,
) -> str:
    """Validate that a string value is not empty.

    Args:
        value: The string value to validate.
        field_name: Name of the field for error messages.
        strip_whitespace: Whether to strip whitespace before validation.

    Returns:
        The validated (and optionally stripped) string.

    Raises:
        ValidationError: If the value is empty or whitespace-only.

    Example:
        >>> name = validate_not_empty("  hello  ", "name")
        >>> print(name)
        hello
    """
    if strip_whitespace:
        value = value.strip()

    if not value:
        raise ValidationError(
            f"'{field_name}' cannot be empty",
            details={"field": field_name, "value": value},
        )

    return value


def validate_url(
    url: str,
    field_name: str = "url",
    require_https: bool = False,
) -> str:
    """Validate that a string is a valid URL.

    Args:
        url: The URL string to validate.
        field_name: Name of the field for error messages.
        require_https: If True, only HTTPS URLs are valid.

    Returns:
        The validated URL string.

    Raises:
        ValidationError: If the URL is invalid or doesn't meet requirements.

    Example:
        >>> url = validate_url("https://example.com/api", "endpoint")
        >>> print(url)
        https://example.com/api
    """
    url = url.strip()

    if not url:
        raise ValidationError(
            f"'{field_name}' cannot be empty",
            details={"field": field_name},
        )

    if require_https and not url.startswith("https://"):
        raise ValidationError(
            f"'{field_name}' must use HTTPS",
            details={"field": field_name, "value": url},
        )

    if not URL_PATTERN.match(url):
        raise ValidationError(
            f"'{field_name}' is not a valid URL",
            details={"field": field_name, "value": url},
        )

    return url


def validate_positive_int(
    value: int,
    field_name: str,
    min_value: int = 1,
    max_value: int | None = None,
) -> int:
    """Validate that an integer is positive and within bounds.

    Args:
        value: The integer value to validate.
        field_name: Name of the field for error messages.
        min_value: Minimum allowed value (default: 1).
        max_value: Maximum allowed value (default: None, no upper limit).

    Returns:
        The validated integer value.

    Raises:
        ValidationError: If the value is out of bounds.

    Example:
        >>> timeout = validate_positive_int(30, "timeout", min_value=1, max_value=300)
        >>> print(timeout)
        30
    """
    if value < min_value:
        raise ValidationError(
            f"'{field_name}' must be at least {min_value}",
            details={"field": field_name, "value": value, "min_value": min_value},
        )

    if max_value is not None and value > max_value:
        raise ValidationError(
            f"'{field_name}' must be at most {max_value}",
            details={"field": field_name, "value": value, "max_value": max_value},
        )

    return value


def validate_in_list(
    value: T,
    allowed_values: list[T],
    field_name: str,
) -> T:
    """Validate that a value is in a list of allowed values.

    Args:
        value: The value to validate.
        allowed_values: List of allowed values.
        field_name: Name of the field for error messages.

    Returns:
        The validated value.

    Raises:
        ValidationError: If the value is not in the allowed list.

    Example:
        >>> status = validate_in_list("active", ["active", "inactive"], "status")
        >>> print(status)
        active
    """
    if value not in allowed_values:
        raise ValidationError(
            f"'{field_name}' must be one of {allowed_values}",
            details={"field": field_name, "value": value, "allowed": allowed_values},
        )

    return value
