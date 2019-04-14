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
        cls.store(event)

        if cls._can_drain():
            await cls.drain()

    @classmethod
    def store(cls, event: types.Event):
        h.heappush(cls._BUFFER, event)

    @classmethod
    async def drain(cls):
        while True:
            event = cls._BUFFER[0]

            if not cls._can_process_event(event):
                break

            cls._BUFFER.pop()
            await cls._process(event)

    @classmethod
    async def _process(cls, event: types.Event):
        # TODO:
        # if isinstance(event, types.Broadcast):
        #     await registry.ClientWriterRegistry.broadcast(event.payload)
        #     cls._LAST_SEQ_NO = event.seq_no

        pass

    @classmethod
    def _can_drain(cls) -> bool:
        if not cls._BUFFER:
            return False

        return cls._can_process_event(cls._BUFFER[0])

    @classmethod
    def _can_process_event(cls, event: types.Event) -> bool:
        print(f"seq_no: {event.seq_no}, last: {cls._LAST_SEQ_NO}, event: {event}")
        if event.seq_no - cls._LAST_SEQ_NO == 1:
            return True

        return False
