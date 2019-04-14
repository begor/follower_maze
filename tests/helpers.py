import asyncio


def async_test(coroutine):
    """
        Run decorated method in a currently active event loop.
    """
    def wrapper(*args, **kwargs):
        loop = asyncio.get_event_loop()
        return loop.run_until_complete(coroutine(*args, **kwargs))

    return wrapper
