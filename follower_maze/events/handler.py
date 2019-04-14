import asyncio
import heapq
from typing import Optional

from follower_maze import clients
from follower_maze.events import types


# Just a facade-like interface for synchronized access to mutable state of a buffer
class EventHandler:
    _BUFFER = []  # Min heap of Events, acts as a buffer
    _LAST_PROCESSED_SEQ_NO = 0  # Last handled seq_no
    _ALOCK = asyncio.Lock()  # Locks critical sections w/ access to _BUFFER
    _STOP = asyncio.Event()

    @classmethod
    async def new(cls, event: types.Event):
        await cls.store(event)
        await cls.drain()

    @classmethod
    async def store(cls, event: types.Event):
        async with cls._ALOCK:
            heapq.heappush(cls._BUFFER, event)

    @classmethod
    async def get_seq_no(cls):
        async with cls._ALOCK:
            return cls._LAST_PROCESSED_SEQ_NO

    @classmethod
    async def reset(cls):
        async with cls._ALOCK:
            cls._BUFFER = []
            cls._LAST_PROCESSED_SEQ_NO = 0  # Last handled seq_no

    @classmethod
    async def drain(cls):
        while True:
            async with cls._ALOCK:
                if not cls._BUFFER:
                    return

                maybe_event = cls._get_processable_event()

                if not maybe_event:
                    return

                event = maybe_event

            await cls._process(event)
            await cls._finalize_event()

    @classmethod
    async def _process(cls, event: types.Event):
        if isinstance(event, types.Broadcast):
            await clients.broadcast(payload=event.payload)

        if isinstance(event, types.Follow):
            await clients.follow(from_client=event.from_user, to_client=event.to_user, payload=event.payload)

        if isinstance(event, types.PrivateMessage):
            await clients.send_private_message(client_id=event.to_user, payload=event.payload)

        if isinstance(event, types.StatusUpdate):
            await clients.send_to_followers(client_id=event.from_user, payload=event.payload)

        if isinstance(event, types.Unfollow):
            await clients.unfollow(from_client=event.from_user, to_client=event.to_user)

    @classmethod
    async def _finalize_event(cls):
        async with cls._ALOCK:
            cls._LAST_PROCESSED_SEQ_NO = heapq.heappop(cls._BUFFER).seq_no

    @classmethod
    def _get_processable_event(cls) -> Optional[types.Event]:
        top_event = cls._BUFFER[0]

        if top_event.seq_no - cls._LAST_PROCESSED_SEQ_NO == 1:
            return top_event

