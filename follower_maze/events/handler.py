import asyncio
import heapq as h

from follower_maze.events import types
from follower_maze.clients import registry


# Just a facade-like interface for synchronized access to mutable state of a buffer
class EventHandler:
    _BUFFER = []  # Min heap of Events
    _LAST_SEQ_NO = 0  # Last handled seq_no
    _ALOCK = asyncio.Lock()  # Locks critical sections w/ access to _BUFFER
    _STOP = asyncio.Event()

    @classmethod
    async def new(cls, event: types.Event):
        async with cls._ALOCK:
            await cls.store(event)
            await cls.drain()

    @classmethod
    async def store(cls, event: types.Event):
        h.heappush(cls._BUFFER, event)

    @classmethod
    async def drain(cls):
        while True:
            if not cls._BUFFER:
                return

            top_event = cls._BUFFER[0]
            if not cls._can_process_event(top_event):
                break

            await cls._process(top_event)
            cls._LAST_SEQ_NO = top_event.seq_no
            h.heappop(cls._BUFFER)

    @classmethod
    async def _process(cls, event: types.Event):
        print(event.seq_no)
        if isinstance(event, types.Broadcast):
            await registry.Clients.notify_all(event.payload)
        elif isinstance(event, types.Follow):
            await registry.Clients.follow(event.from_user, event.to_user)
            await registry.Clients.notify(event.to_user, event.payload)
        elif isinstance(event, types.PrivateMessage):
            await registry.Clients.notify(event.to_user, event.payload)
        elif isinstance(event, types.StatusUpdate):
            await registry.Clients.notify_followers(event.from_user, event.payload)
        elif isinstance(event, types.Unfollow):
            await registry.Clients.unfollow(event.from_user, event.to_user)

    @classmethod
    async def _finalize_event(cls, event: types.Event):
        cls._LAST_SEQ_NO = event.seq_no
        h.heappop(cls._BUFFER)

    @classmethod
    def _can_process_event(cls, event: types.Event) -> bool:
        if event.seq_no - cls._LAST_SEQ_NO == 1:
            return True

        return False
