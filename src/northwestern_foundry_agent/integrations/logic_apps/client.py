"""Logic Apps client for triggering workflows.

This module provides a client for invoking Logic App HTTP triggers
with proper error handling and retry logic.
"""

from __future__ import annotations

from typing import Any

import httpx

from northwestern_foundry_agent.config.settings import Settings, get_settings
from northwestern_foundry_agent.integrations.logic_apps.models import (
    LogicAppRequest,
    LogicAppResponse,
)
from northwestern_foundry_agent.utils.errors import ConfigurationError, LogicAppError
from northwestern_foundry_agent.utils.logging import get_logger
from northwestern_foundry_agent.utils.retry import retry_async

logger = get_logger(__name__)


class LogicAppsClient:
    """Client for invoking Logic App workflows.

    Provides methods to trigger Logic App HTTP endpoints with
    error handling and retry logic.

    Attributes:
        settings: Application settings instance.
        trigger_url: HTTP trigger URL for the Logic App.
        sas_token: Optional SAS token for authentication.

    Example:
        >>> client = LogicAppsClient()
        >>> request = LogicAppRequest(action="process", input_data={"key": "value"})
        >>> response = await client.trigger(request)
        >>> print(response.status)
        succeeded
    """

    def __init__(
        self,
        settings: Settings | None = None,
        trigger_url: str | None = None,
        sas_token: str | None = None,
        timeout: float = 60.0,
    ) -> None:
        """Initialize the Logic Apps client.

        Args:
            settings: Optional Settings instance.
            trigger_url: Override trigger URL.
            sas_token: Override SAS token for authentication.
            timeout: HTTP request timeout in seconds.

        Raises:
            ConfigurationError: If trigger URL is not configured.
        """
        self.settings = settings or get_settings()
        self.trigger_url = trigger_url or self.settings.logic_app_trigger_url
        self.sas_token = sas_token or self.settings.logic_app_sas_token
        self.timeout = timeout

        if not self.trigger_url:
            raise ConfigurationError(
                "Logic App trigger URL is not configured",
                details={"setting": "logic_app_trigger_url"},
            )

        logger.info("Logic Apps client initialized")

    def _get_headers(self) -> dict[str, str]:
        """Get HTTP headers for trigger calls.

        Returns:
            Dictionary of HTTP headers.
        """
        headers: dict[str, str] = {
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

        if self.sas_token:
            headers["Authorization"] = f"Bearer {self.sas_token}"

        return headers

    @retry_async(max_attempts=3, exceptions=(LogicAppError,))
    async def trigger(
        self,
        request: LogicAppRequest,
    ) -> LogicAppResponse:
        """Trigger the Logic App workflow.

        Args:
            request: LogicAppRequest with action and input data.

        Returns:
            LogicAppResponse with workflow result.

        Raises:
            LogicAppError: If the trigger fails.

        Example:
            >>> request = LogicAppRequest(
            ...     action="process_document",
            ...     input_data={"document_id": "doc123"}
            ... )
            >>> response = await client.trigger(request)
        """
        logger.info(
            "Triggering Logic App: action=%s, correlation_id=%s",
            request.action,
            request.correlation_id,
        )

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                response = await client.post(
                    self.trigger_url,
                    headers=self._get_headers(),
                    json=request.to_trigger_payload(),
                )

                response.raise_for_status()

                # Parse response
                data = response.json()
                return LogicAppResponse.model_validate(data)

            except httpx.HTTPStatusError as e:
                logger.error(
                    "Logic App returned error: status=%d",
                    e.response.status_code,
                )
                raise LogicAppError(
                    f"Logic App returned error: {e.response.status_code}",
                    status_code=e.response.status_code,
                    details={"response_text": e.response.text[:500]},
                ) from e

            except httpx.RequestError as e:
                logger.error("Request to Logic App failed: %s", str(e))
                raise LogicAppError(
                    f"Request failed: {e}",
                ) from e

    async def trigger_and_wait(
        self,
        request: LogicAppRequest,
        poll_interval: float = 5.0,
        max_wait: float = 300.0,
    ) -> LogicAppResponse:
        """Trigger the Logic App and wait for completion.

        For long-running workflows, this method polls for completion.

        Args:
            request: LogicAppRequest with action and input data.
            poll_interval: Seconds between status polls.
            max_wait: Maximum seconds to wait for completion.

        Returns:
            LogicAppResponse with final workflow result.

        Raises:
            LogicAppError: If the workflow fails or times out.
        """
        import asyncio

        response = await self.trigger(request)

        elapsed = 0.0
        while response.is_running and elapsed < max_wait:
            await asyncio.sleep(poll_interval)
            elapsed += poll_interval
            logger.debug(
                "Waiting for workflow completion: elapsed=%.1fs",
                elapsed,
            )

        if response.is_running:
            raise LogicAppError(
                f"Workflow timed out after {max_wait} seconds",
                details={"workflow_run_id": response.workflow_run_id},
            )

        return response

    def trigger_sync(self, request: LogicAppRequest) -> LogicAppResponse:
        """Synchronous version of trigger.

        Args:
            request: LogicAppRequest with action and input data.

        Returns:
            LogicAppResponse with workflow result.

        Raises:
            LogicAppError: If the trigger fails.
        """
        import asyncio

        return asyncio.get_event_loop().run_until_complete(self.trigger(request))


def create_logic_app_handler(client: LogicAppsClient) -> Any:
    """Create a tool handler function for use with FoundryAgent.

    Creates a synchronous handler function that can be registered
    with the FoundryAgent for tool invocations.

    Args:
        client: LogicAppsClient instance.

    Returns:
        Handler function for Logic App tool calls.

    Example:
        >>> client = LogicAppsClient()
        >>> handler = create_logic_app_handler(client)
        >>> agent.register_tool(logic_app_tool, handler)
    """

    def logic_app_handler(input_data: dict[str, Any]) -> dict[str, Any]:
        """Handler for Logic App tool calls."""
        request = LogicAppRequest(
            action="agent_request",
            input_data=input_data,
        )
        response = client.trigger_sync(request)
        return response.model_dump()

    return logic_app_handler
