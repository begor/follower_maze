import asyncio
import heapq as h

from follower_maze.events import types
from follower_maze.clients import registry


# TODO: locking
# Just a facade-like interface for synchronized access to mutable state of a buffer
class EventHandler:
    _BUFFER = []  # Min heap of Events
    _LAST_SEQ_NO = 0  # Last handled seq_no
    _ALOCK = asyncio.Lock()  # Locks critical sections w/ access to _BUFFER

    @classmethod
    async def new(cls, event: types.Event):
        await cls.store(event)
        await cls.drain()

    @classmethod
    async def store(cls, event: types.Event):
        async with cls._ALOCK:
            h.heappush(cls._BUFFER, event)

    @classmethod
    async def drain(cls):
        while True:
            async with cls._ALOCK:
                if not cls._BUFFER:
                    return

                event = cls._BUFFER[0]
                if not cls._can_process_event(event):
                    break

                cls._LAST_SEQ_NO = event.seq_no
                h.heappop(cls._BUFFER)

            await cls._process(event)

    @classmethod
    async def _process(cls, event: types.Event):
        if isinstance(event, (types.Follow, types.PrivateMessage)):
            await registry.Clients.notify(event.to_user, event.payload)
        if isinstance(event, types.Broadcast):
            await registry.Clients.notify_all(event.payload)


    @classmethod
    def _can_process_event(cls, event: types.Event) -> bool:
        if event.seq_no - cls._LAST_SEQ_NO == 1:
            return True

        return False
