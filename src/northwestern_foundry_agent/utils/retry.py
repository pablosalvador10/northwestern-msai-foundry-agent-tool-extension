"""Retry utilities for robust network operations.

This module provides decorators for adding retry logic to synchronous
and asynchronous functions, with exponential backoff and jitter.
"""

from __future__ import annotations

import asyncio
from collections.abc import Awaitable, Callable
from functools import wraps
from typing import ParamSpec, TypeVar

from tenacity import (
    AsyncRetrying,
    RetryError,
    Retrying,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential_jitter,
)

from northwestern_foundry_agent.utils.logging import get_logger

logger = get_logger(__name__)

P = ParamSpec("P")
T = TypeVar("T")


# Default retry configuration
DEFAULT_MAX_ATTEMPTS = 3
DEFAULT_WAIT_MIN = 1
DEFAULT_WAIT_MAX = 10
DEFAULT_JITTER_MAX = 2


def retry_sync(
    max_attempts: int = DEFAULT_MAX_ATTEMPTS,
    wait_min: float = DEFAULT_WAIT_MIN,
    wait_max: float = DEFAULT_WAIT_MAX,
    jitter_max: float = DEFAULT_JITTER_MAX,
    exceptions: tuple[type[Exception], ...] = (Exception,),
) -> Callable[[Callable[P, T]], Callable[P, T]]:
    """Decorator to add retry logic to synchronous functions.

    Retries the decorated function on failure with exponential backoff
    and jitter to prevent thundering herd problems.

    Args:
        max_attempts: Maximum number of retry attempts.
        wait_min: Minimum wait time between retries in seconds.
        wait_max: Maximum wait time between retries in seconds.
        jitter_max: Maximum random jitter to add to wait time.
        exceptions: Tuple of exception types to retry on.

    Returns:
        Decorated function with retry logic.

    Example:
        >>> @retry_sync(max_attempts=3, exceptions=(ConnectionError,))
        ... def fetch_data() -> dict:
        ...     # Function that might fail transiently
        ...     return {"data": "value"}
    """

    def decorator(func: Callable[P, T]) -> Callable[P, T]:
        @wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
            try:
                for attempt in Retrying(
                    stop=stop_after_attempt(max_attempts),
                    wait=wait_exponential_jitter(initial=wait_min, max=wait_max, jitter=jitter_max),
                    retry=retry_if_exception_type(exceptions),
                    reraise=True,
                ):
                    with attempt:
                        if attempt.retry_state.attempt_number > 1:
                            logger.warning(
                                "Retrying %s (attempt %d/%d)",
                                func.__name__,
                                attempt.retry_state.attempt_number,
                                max_attempts,
                            )
                        return func(*args, **kwargs)
            except RetryError as e:
                logger.error(
                    "All retry attempts failed for %s: %s",
                    func.__name__,
                    str(e.last_attempt.exception()),
                )
                raise
            # This should never be reached due to reraise=True
            raise RuntimeError("Unexpected retry state")  # pragma: no cover

        return wrapper

    return decorator


def retry_async(
    max_attempts: int = DEFAULT_MAX_ATTEMPTS,
    wait_min: float = DEFAULT_WAIT_MIN,
    wait_max: float = DEFAULT_WAIT_MAX,
    jitter_max: float = DEFAULT_JITTER_MAX,
    exceptions: tuple[type[Exception], ...] = (Exception,),
) -> Callable[[Callable[P, Awaitable[T]]], Callable[P, Awaitable[T]]]:
    """Decorator to add retry logic to asynchronous functions.

    Retries the decorated async function on failure with exponential backoff
    and jitter to prevent thundering herd problems.

    Args:
        max_attempts: Maximum number of retry attempts.
        wait_min: Minimum wait time between retries in seconds.
        wait_max: Maximum wait time between retries in seconds.
        jitter_max: Maximum random jitter to add to wait time.
        exceptions: Tuple of exception types to retry on.

    Returns:
        Decorated async function with retry logic.

    Example:
        >>> @retry_async(max_attempts=3, exceptions=(httpx.HTTPError,))
        ... async def fetch_data_async() -> dict:
        ...     async with httpx.AsyncClient() as client:
        ...         response = await client.get("https://api.example.com/data")
        ...         return response.json()
    """

    def decorator(func: Callable[P, Awaitable[T]]) -> Callable[P, Awaitable[T]]:
        @wraps(func)
        async def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
            try:
                async for attempt in AsyncRetrying(
                    stop=stop_after_attempt(max_attempts),
                    wait=wait_exponential_jitter(initial=wait_min, max=wait_max, jitter=jitter_max),
                    retry=retry_if_exception_type(exceptions),
                    reraise=True,
                ):
                    with attempt:
                        if attempt.retry_state.attempt_number > 1:
                            logger.warning(
                                "Retrying %s (attempt %d/%d)",
                                func.__name__,
                                attempt.retry_state.attempt_number,
                                max_attempts,
                            )
                        return await func(*args, **kwargs)
            except RetryError as e:
                logger.error(
                    "All retry attempts failed for %s: %s",
                    func.__name__,
                    str(e.last_attempt.exception()),
                )
                raise
            # This should never be reached due to reraise=True
            raise RuntimeError("Unexpected retry state")  # pragma: no cover

        return wrapper

    return decorator


async def retry_with_timeout(
    coro_factory: Callable[[], Awaitable[T]],
    timeout: float,
    max_attempts: int = DEFAULT_MAX_ATTEMPTS,
) -> T:
    """Execute an awaitable with timeout and retry logic.

    Combines timeout and retry functionality for network operations
    that may hang or fail transiently.

    Args:
        coro_factory: A callable that returns a coroutine to execute.
        timeout: Timeout in seconds for each attempt.
        max_attempts: Maximum number of retry attempts.

    Returns:
        Result of the awaitable.

    Raises:
        asyncio.TimeoutError: If all attempts time out.
        Exception: If all attempts fail with non-timeout errors.

    Example:
        >>> async def make_request():
        ...     return await fetch_data_async()
        >>> result = await retry_with_timeout(
        ...     make_request,  # Pass a callable, not a coroutine
        ...     timeout=5.0,
        ...     max_attempts=3
        ... )
    """
    last_exception: Exception | None = None

    for attempt in range(1, max_attempts + 1):
        try:
            # coro_factory should be a callable that returns a coroutine
            return await asyncio.wait_for(coro_factory(), timeout=timeout)
        except TimeoutError:
            logger.warning(
                "Attempt %d/%d timed out after %.1f seconds",
                attempt,
                max_attempts,
                timeout,
            )
            last_exception = TimeoutError()
        except Exception as e:
            logger.warning(
                "Attempt %d/%d failed: %s",
                attempt,
                max_attempts,
                str(e),
            )
            last_exception = e

    if last_exception:
        raise last_exception
    raise RuntimeError("Unexpected retry state")  # pragma: no cover
