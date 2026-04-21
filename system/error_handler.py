"""
Error handling decorator for AllTalk TTS application.

This module provides a decorator for consistent error handling across the application.
"""

import asyncio

from functools import wraps

from loguru import logger

from system.exceptions import AllTalkError


def handle_errors(component: str = "TTS"):
    """
    Decorator for consistent error handling.

    Args:
        component: Component name for logging (e.g., "TTS", "API", "Config")

    Returns:
        Decorator function that wraps sync or async functions
    """

    def decorator(func):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            try:
                return await func(*args, **kwargs)
            except AllTalkError as e:
                logger.error(f"[{component}] {type(e).__name__}: {e}")
                raise
            except Exception as e:
                logger.exception(f"[{component}] Unexpected error in {func.__name__}")
                raise AllTalkError(f"Unexpected error: {e}") from e

        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except AllTalkError as e:
                logger.error(f"[{component}] {type(e).__name__}: {e}")
                raise
            except Exception as e:
                logger.exception(f"[{component}] Unexpected error in {func.__name__}")
                raise AllTalkError(f"Unexpected error: {e}") from e

        return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper

    return decorator
