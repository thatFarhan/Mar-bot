# credits to indently.io
import asyncio
from functools import wraps
from typing import Callable, Any
from time import sleep

def retry(retries: int = 3, delay: float = 1) -> Callable:
    """
    Attempt to call a function, if it fails, try again with a specified delay.

    :param retries: The max amount of retries you want for the function call
    :param delay: The delay (in seconds) between each function retry
    :return:
    """
    if retries < 1 or delay <= 0:
        raise ValueError('Are you high, mate?')

    def decorator(func: Callable) -> Callable:

        if asyncio.iscoroutinefunction(func):
            @wraps(func)
            async def async_wrapper(*args, **kwargs) -> Any:
                for i in range(1, retries + 1):
                    try:
                        print(f'Running ({i}): {func.__name__}()')
                        return await func(*args, **kwargs)
                    except Exception as e:
                        if i == retries:
                            print(f'Error: {repr(e)}.')
                            print(f'"{func.__name__}()" failed after {retries} retries.')
                            break
                        else:
                            print(f'Error: {repr(e)} -> Retrying...')
                            await asyncio.sleep(delay)
            return async_wrapper

        else:
            @wraps(func)
            def sync_wrapper(*args, **kwargs) -> Any:
                for i in range(1, retries + 1):
                    try:
                        print(f'Running ({i}): {func.__name__}()')
                        return func(*args, **kwargs)
                    except Exception as e:
                        if i == retries:
                            print(f'Error: {repr(e)}.')
                            print(f'"{func.__name__}()" failed after {retries} retries.')
                            break
                        else:
                            print(f'Error: {repr(e)} -> Retrying...')
                            sleep(delay)
            return sync_wrapper

    return decorator