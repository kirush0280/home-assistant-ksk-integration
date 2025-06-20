"""КСК decorators."""
from __future__ import annotations

import asyncio
from collections.abc import Awaitable, Callable, Coroutine
from functools import wraps
from random import randrange
from typing import TYPE_CHECKING, Any, Concatenate, ParamSpec, TypeVar

from homeassistant.exceptions import ConfigEntryAuthFailed
from homeassistant.helpers.update_coordinator import UpdateFailed

from .const import API_MAX_TRIES, API_RETRY_DELAY, API_TIMEOUT
from .exceptions import CannotConnect, InvalidAuth

if TYPE_CHECKING:
    pass

_KskCoordinatorT = TypeVar("_KskCoordinatorT", bound="KskCoordinator")
_R = TypeVar("_R")
_P = ParamSpec("_P")


def async_api_request_handler(
        method: Callable[Concatenate[_KskCoordinatorT, _P], Awaitable[_R]],
) -> Callable[Concatenate[_KskCoordinatorT, _P], Coroutine[Any, Any, _R]]:
    """Handle API errors."""

    @wraps(method)
    async def wrapper(
            self: _KskCoordinatorT, *args: _P.args, **kwargs: _P.kwargs
    ) -> _R:
        """Wrap an API method."""
        try:
            tries = 0
            api_timeout = API_TIMEOUT
            api_retry_delay = API_RETRY_DELAY
            while True:
                tries += 1
                try:
                    async with asyncio.timeout(api_timeout):
                        result = await method(self, *args, **kwargs)

                    if result is not None:
                        return result

                    self.logger.error(
                        "API error while execute function %s", method.__name__
                    )
                    raise CannotConnect(
                        f"API error while execute function {method.__name__}"
                    )

                except TimeoutError:
                    api_timeout = tries * API_TIMEOUT
                    self.logger.debug(
                        "Function %s: Timeout connecting to КСК", method.__name__
                    )

                if tries >= API_MAX_TRIES:
                    raise CannotConnect(
                        f"API error while execute function {method.__name__}"
                    )

                self.logger.warning(
                    "Attempt %d/%d. Wait %d seconds and try again",
                    tries,
                    API_MAX_TRIES,
                    api_retry_delay,
                )
                await asyncio.sleep(api_retry_delay)
                api_retry_delay += API_RETRY_DELAY + randrange(API_RETRY_DELAY)

        except InvalidAuth as exc:
            raise ConfigEntryAuthFailed("КСК auth error") from exc
        except CannotConnect as exc:
            raise UpdateFailed(f"Invalid response from КСК API: {exc}") from exc

    return wrapper 