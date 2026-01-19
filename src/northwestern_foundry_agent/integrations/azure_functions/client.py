"""Azure Functions client for invoking HTTP-triggered functions.

This module provides a client for calling Azure Functions endpoints
with proper authentication, error handling, and retry logic.
"""

from __future__ import annotations

from typing import Any

import httpx

from northwestern_foundry_agent.config.settings import Settings, get_settings
from northwestern_foundry_agent.integrations.azure_functions.models import (
    HealthCheckResponse,
    QuoteResponse,
)
from northwestern_foundry_agent.utils.errors import (
    ConfigurationError,
    FunctionInvocationError,
)
from northwestern_foundry_agent.utils.logging import get_logger
from northwestern_foundry_agent.utils.retry import retry_async

logger = get_logger(__name__)


class AzureFunctionsClient:
    """Client for invoking Azure Functions.

    Provides methods to call Azure Function HTTP endpoints with
    authentication, error handling, and retry logic.

    Attributes:
        settings: Application settings instance.
        base_url: Base URL for the Azure Functions app.
        function_key: Function key for authentication.

    Example:
        >>> client = AzureFunctionsClient()
        >>> health = await client.health_check()
        >>> print(health.status)
        healthy
    """

    def __init__(
        self,
        settings: Settings | None = None,
        base_url: str | None = None,
        function_key: str | None = None,
        timeout: float = 30.0,
    ) -> None:
        """Initialize the Azure Functions client.

        Args:
            settings: Optional Settings instance.
            base_url: Override base URL for the Functions app.
            function_key: Override function key for authentication.
            timeout: HTTP request timeout in seconds.

        Raises:
            ConfigurationError: If base URL is not configured.
        """
        self.settings = settings or get_settings()
        self.base_url = base_url or self.settings.azure_function_app_url
        self.function_key = function_key or self.settings.azure_function_key
        self.timeout = timeout

        if not self.base_url:
            raise ConfigurationError(
                "Azure Functions base URL is not configured",
                details={"setting": "azure_function_app_url"},
            )

        # Ensure base URL doesn't have trailing slash
        self.base_url = self.base_url.rstrip("/")

        logger.info("Azure Functions client initialized: base_url=%s", self.base_url)

    def _get_headers(self) -> dict[str, str]:
        """Get HTTP headers for function calls.

        Returns:
            Dictionary of HTTP headers.
        """
        headers: dict[str, str] = {
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

        if self.function_key:
            headers["x-functions-key"] = self.function_key

        return headers

    async def _make_request(
        self,
        method: str,
        endpoint: str,
        params: dict[str, Any] | None = None,
        json_data: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Make an HTTP request to an Azure Function.

        Args:
            method: HTTP method (GET, POST, etc.).
            endpoint: Function endpoint path.
            params: Optional query parameters.
            json_data: Optional JSON body data.

        Returns:
            Response data as dictionary.

        Raises:
            FunctionInvocationError: If the request fails.
        """
        url = f"{self.base_url}/api/{endpoint.lstrip('/')}"

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                response = await client.request(
                    method=method,
                    url=url,
                    headers=self._get_headers(),
                    params=params,
                    json=json_data,
                )

                response.raise_for_status()
                result: dict[str, Any] = response.json()
                return result

            except httpx.HTTPStatusError as e:
                logger.error(
                    "Function returned error: endpoint=%s, status=%d",
                    endpoint,
                    e.response.status_code,
                )
                raise FunctionInvocationError(
                    f"Function returned error: {e.response.status_code}",
                    function_name=endpoint,
                    status_code=e.response.status_code,
                    details={"response_text": e.response.text[:500]},
                ) from e

            except httpx.RequestError as e:
                logger.error(
                    "Request failed: endpoint=%s, error=%s",
                    endpoint,
                    str(e),
                )
                raise FunctionInvocationError(
                    f"Request failed: {e}",
                    function_name=endpoint,
                ) from e

    @retry_async(max_attempts=3, exceptions=(FunctionInvocationError,))
    async def health_check(self) -> HealthCheckResponse:
        """Call the health check function.

        Returns:
            HealthCheckResponse with status information.

        Raises:
            FunctionInvocationError: If the health check fails.

        Example:
            >>> health = await client.health_check()
            >>> if health.is_healthy:
            ...     print("Service is healthy")
        """
        logger.info("Calling health check function")
        data = await self._make_request("GET", "health")
        return HealthCheckResponse.model_validate(data)

    @retry_async(max_attempts=3, exceptions=(FunctionInvocationError,))
    async def quote_of_the_day(
        self,
        category: str = "motivation",
    ) -> QuoteResponse:
        """Call the quote of the day function.

        Args:
            category: Category of quote (motivation, wisdom, humor).

        Returns:
            QuoteResponse with the quote data.

        Raises:
            FunctionInvocationError: If the function call fails.

        Example:
            >>> quote = await client.quote_of_the_day(category="wisdom")
            >>> print(f"'{quote.quote}' - {quote.author}")
        """
        logger.info("Calling quote function: category=%s", category)
        data = await self._make_request(
            "GET",
            "quote",
            params={"category": category},
        )
        return QuoteResponse.model_validate(data)

    def health_check_sync(self) -> HealthCheckResponse:
        """Synchronous version of health_check.

        Returns:
            HealthCheckResponse with status information.

        Raises:
            FunctionInvocationError: If the health check fails.
        """
        import asyncio

        try:
            asyncio.get_running_loop()
        except RuntimeError:
            # No running loop, create one
            result: HealthCheckResponse = asyncio.run(
                self.health_check()  # type: ignore[arg-type]
            )
            return result
        else:
            # Running in async context - this is unusual but handle it
            import warnings

            warnings.warn(
                "Calling sync method from async context. Consider using the async method.",
                stacklevel=2,
            )
            # Create a new event loop for this call
            loop = asyncio.new_event_loop()
            try:
                return loop.run_until_complete(self.health_check())
            finally:
                loop.close()

    def quote_of_the_day_sync(
        self,
        category: str = "motivation",
    ) -> QuoteResponse:
        """Synchronous version of quote_of_the_day.

        Args:
            category: Category of quote.

        Returns:
            QuoteResponse with the quote data.

        Raises:
            FunctionInvocationError: If the function call fails.
        """
        import asyncio

        try:
            asyncio.get_running_loop()
        except RuntimeError:
            # No running loop, create one
            result: QuoteResponse = asyncio.run(
                self.quote_of_the_day(category)  # type: ignore[arg-type]
            )
            return result
        else:
            # Running in async context - this is unusual but handle it
            import warnings

            warnings.warn(
                "Calling sync method from async context. Consider using the async method.",
                stacklevel=2,
            )
            # Create a new event loop for this call
            loop = asyncio.new_event_loop()
            try:
                return loop.run_until_complete(self.quote_of_the_day(category))
            finally:
                loop.close()


def create_function_handlers(client: AzureFunctionsClient) -> dict[str, Any]:
    """Create tool handler functions for use with FoundryAgent.

    Creates synchronous handler functions that can be registered
    with the FoundryAgent for tool invocations.

    Args:
        client: AzureFunctionsClient instance.

    Returns:
        Dictionary mapping tool names to handler functions.

    Example:
        >>> client = AzureFunctionsClient()
        >>> handlers = create_function_handlers(client)
        >>> agent.register_tool(health_tool, handlers["health_check"])
    """

    def health_check_handler() -> dict[str, Any]:
        """Handler for health_check tool calls."""
        response = client.health_check_sync()
        return response.model_dump()

    def quote_handler(category: str = "motivation") -> dict[str, Any]:
        """Handler for quote_of_the_day tool calls."""
        response = client.quote_of_the_day_sync(category)
        return response.model_dump()

    return {
        "health_check": health_check_handler,
        "quote_of_the_day": quote_handler,
    }
