import asyncio
from collections import defaultdict
from typing import Optional

import logging

LOG = logging.getLogger(__name__)


class Clients:
    """
        Registry-like facade for keeping track and notifying clients.

        Uses two hash maps for storing clients:
            - `_REGISTRY` maps `client_id` to `client_writer` (via witch client might be notified)
            - `_FOLLOWERS` maps `client_id` to its followers

        Every time we fetch client_id from `_REGISTRY`, we check whether its `client_writer` if alive (not closed).
        If it's closed, we discard that client and every notify to it in future will be silently omitted.

        NOTES:
            - Assumes no duplicate client
            - Assumes that number of concurrently connected clients can fit in memory
    """
    _REGISTRY = {}
    _FOLLOWERS = defaultdict(set)
    _ALOCK = asyncio.Lock()

    @classmethod
    async def reset(cls):
        async with cls._ALOCK:
            cls._REGISTRY = {}
            cls._FOLLOWERS = defaultdict(set)

    @classmethod
    async def register(cls, client_id: int, writer: asyncio.StreamWriter):
        LOG.debug(f"{client_id} is online")

        async with cls._ALOCK:
            cls._REGISTRY[client_id] = writer

    @classmethod
    async def maybe_get_client_writer(cls, client_id: int) -> Optional[asyncio.StreamWriter]:
        async with cls._ALOCK:
            maybe_writer = cls._REGISTRY.get(client_id)

        if maybe_writer is None:
            return

        if maybe_writer.is_closing():
            await cls.delete(client_id)
            return

        return maybe_writer

    @classmethod
    async def delete(cls, client_id: int):
        LOG.debug(f"{client_id} is gone")

        async with cls._ALOCK:
            if client_id in cls._REGISTRY:
                cls._REGISTRY.pop(client_id)
            if client_id in cls._FOLLOWERS:
                cls._FOLLOWERS.pop(client_id)

    @classmethod
    async def follow(cls, from_client_id: int, to_client_id: int):
        async with cls._ALOCK:
            cls._FOLLOWERS[to_client_id].add(from_client_id)

    @classmethod
    async def unfollow(cls, from_client_id: int, to_client_id: int):
        async with cls._ALOCK:
            cls._FOLLOWERS[to_client_id].discard(from_client_id)

    @classmethod
    async def notify(cls, client_id: int, payload: bytes):
        maybe_client_writer = await cls.maybe_get_client_writer(client_id)

        if maybe_client_writer is None:
            return

        LOG.debug(f"Notifying {client_id}")

        client_writer = maybe_client_writer
        client_writer.write(payload)

    @classmethod
    async def notify_all(cls, payload: bytes):
        async with cls._ALOCK:
            clients = list(cls._REGISTRY.keys())

        LOG.debug(f"Notifying all {len(clients)}")

        for client_id in clients:
            await cls.notify(client_id, payload)

    @classmethod
    async def notify_followers(cls, from_user_id: int, payload: bytes):
        async with cls._ALOCK:
            followers = list(cls._FOLLOWERS[from_user_id])

        LOG.debug(f"Notifying {len(followers)} of {from_user_id}")

        if not followers:
            return

        for client_id in followers:
            await cls.notify(client_id, payload)
