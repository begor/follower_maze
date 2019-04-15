import asyncio
import heapq
from typing import Optional

from follower_maze import clients
from follower_maze.events import types


class EventHandler:
    """
        Facade for handling incoming stream of events.

        Two main goals:
            - Order events by their seq_no's using `_BUFFER` (see details below).
            - Process events STRICTLY in order using `client` module.

        NOTES:
            - Using MinHeap for ordering (O(logN) complexity for pushing while preserving order)
            - Assumes that out-of-order events batch size fits in memory
            - Assumes source without duplicates.
              If source can produce duplicates it's easy to add de-duplication functionality here.
    """
    _BUFFER = []  # Min heap of Events, acts as a buffer
    _LAST_PROCESSED_SEQ_NO = 0  # Last handled seq_no
    _ALOCK = asyncio.Lock()  # Locks critical sections w/ access to _BUFFER

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
        """
            Drain `_BUFFER`, processing every one that if "processable" (see `_get_processable_event` for details).
        """
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
        """
            Dispatch event by type (too bad we don't have pattern matching in Python :)).
        """
        if isinstance(event, types.Broadcast):
            await clients.broadcast(payload=event.payload)

        if isinstance(event, types.Follow):
            await clients.follow(from_client=event.from_user, to_client=event.to_user, payload=event.payload)

        if isinstance(event, types.PrivateMessage):
            await clients.send_private_message(client_id=event.to_user, payload=event.payload)

        if isinstance(event, types.StatusUpdate):
            await clients.status_update(client_id=event.from_user, payload=event.payload)

        if isinstance(event, types.Unfollow):
            await clients.unfollow(from_client=event.from_user, to_client=event.to_user)

    @classmethod
    async def _finalize_event(cls):
        async with cls._ALOCK:
            cls._LAST_PROCESSED_SEQ_NO = heapq.heappop(cls._BUFFER).seq_no

    @classmethod
    def _get_processable_event(cls) -> Optional[types.Event]:
        """
            We can process event if it's seq_no bigger than `_LAST_PROCESSED_SEQ_NO` by one.
        """
        top_event = cls._BUFFER[0]

        if top_event.seq_no - cls._LAST_PROCESSED_SEQ_NO == 1:
            return top_event

