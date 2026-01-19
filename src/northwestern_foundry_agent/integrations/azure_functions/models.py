"""Data models for Azure Functions responses.

This module defines Pydantic models for validating and parsing
responses from Azure Functions.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class FunctionResponse(BaseModel):
    """Base model for Azure Function responses.

    Attributes:
        success: Whether the function executed successfully.
        message: Optional message from the function.
        data: Optional data payload.
        timestamp: Timestamp of the response.
    """

    success: bool = Field(default=True, description="Whether the function succeeded")
    message: str = Field(default="", description="Response message")
    data: dict[str, Any] | None = Field(default=None, description="Response data payload")
    timestamp: datetime = Field(
        default_factory=datetime.utcnow,
        description="Response timestamp",
    )


class HealthCheckResponse(BaseModel):
    """Response model for health check function.

    Attributes:
        status: Health status (healthy, degraded, unhealthy).
        service_name: Name of the service being checked.
        version: Service version string.
        timestamp: Timestamp of the health check.
        details: Additional health check details.
    """

    status: str = Field(description="Health status")
    service_name: str = Field(default="azure-functions", description="Service name")
    version: str = Field(default="1.0.0", description="Service version")
    timestamp: datetime = Field(
        default_factory=datetime.utcnow,
        description="Health check timestamp",
    )
    details: dict[str, Any] = Field(
        default_factory=dict,
        description="Additional health details",
    )

    @property
    def is_healthy(self) -> bool:
        """Check if the service is healthy."""
        return self.status.lower() == "healthy"


class QuoteResponse(BaseModel):
    """Response model for quote of the day function.

    Attributes:
        quote: The quote text.
        author: Author of the quote.
        category: Category of the quote.
        timestamp: Timestamp of the response.
    """

    quote: str = Field(description="The quote text")
    author: str = Field(description="Quote author")
    category: str = Field(default="motivation", description="Quote category")
    timestamp: datetime = Field(
        default_factory=datetime.utcnow,
        description="Response timestamp",
    )
