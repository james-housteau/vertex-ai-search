"""Simplified retry logic using standard approaches."""

import time
from functools import wraps
from typing import Callable, Any, TypeVar, Type, Tuple, cast

F = TypeVar("F", bound=Callable[..., Any])


def retry_with_backoff(
    max_retries: int = 3,
    base_delay: float = 1.0,
    exceptions: Tuple[Type[Exception], ...] = (Exception,),
) -> Callable[[F], F]:
    """Simplified decorator for retrying operations with exponential backoff."""

    def decorator(func: F) -> F:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            delay = base_delay

            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    if attempt == max_retries:
                        raise e
                    time.sleep(delay)
                    delay *= 2

        return cast(F, wrapper)

    return decorator
