"""Data models for Logic Apps requests and responses.

This module defines Pydantic models for validating and parsing
data exchanged with Logic Apps workflows.
"""

from __future__ import annotations

from datetime import UTC, datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class WorkflowStatus(str, Enum):
    """Logic App workflow execution status."""

    PENDING = "pending"
    RUNNING = "running"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    CANCELLED = "cancelled"


class LogicAppRequest(BaseModel):
    """Request model for Logic App HTTP triggers.

    This model defines the expected input schema for Logic App
    workflows triggered via HTTP.

    Attributes:
        action: The action to perform.
        input_data: Input data for the workflow.
        correlation_id: Optional correlation ID for tracking.
        metadata: Optional metadata dictionary.
    """

    action: str = Field(description="Action to perform in the workflow")
    input_data: dict[str, Any] = Field(
        default_factory=dict,
        description="Input data for the workflow",
    )
    correlation_id: str | None = Field(
        default=None,
        description="Correlation ID for request tracking",
    )
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Additional metadata",
    )

    def to_trigger_payload(self) -> dict[str, Any]:
        """Convert to Logic App trigger payload format.

        Returns:
            Dictionary formatted for Logic App HTTP trigger.
        """
        return {
            "action": self.action,
            "inputData": self.input_data,
            "correlationId": self.correlation_id,
            "metadata": self.metadata,
            "timestamp": datetime.now(UTC).isoformat(),
        }


class LogicAppResponse(BaseModel):
    """Response model for Logic App workflow results.

    Attributes:
        workflow_run_id: Unique identifier for the workflow run.
        status: Workflow execution status.
        output_data: Output data from the workflow.
        error: Error information if workflow failed.
        started_at: Workflow start timestamp.
        completed_at: Workflow completion timestamp.
    """

    workflow_run_id: str | None = Field(
        default=None,
        description="Unique workflow run identifier",
    )
    status: WorkflowStatus = Field(
        default=WorkflowStatus.SUCCEEDED,
        description="Workflow execution status",
    )
    output_data: dict[str, Any] = Field(
        default_factory=dict,
        description="Output data from the workflow",
    )
    error: str | None = Field(
        default=None,
        description="Error message if workflow failed",
    )
    started_at: datetime | None = Field(
        default=None,
        description="Workflow start timestamp",
    )
    completed_at: datetime | None = Field(
        default=None,
        description="Workflow completion timestamp",
    )

    @property
    def is_successful(self) -> bool:
        """Check if the workflow completed successfully."""
        return self.status == WorkflowStatus.SUCCEEDED

    @property
    def is_running(self) -> bool:
        """Check if the workflow is still running."""
        return self.status in (WorkflowStatus.PENDING, WorkflowStatus.RUNNING)
