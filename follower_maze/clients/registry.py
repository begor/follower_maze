import asyncio
from collections import defaultdict
from typing import Optional


# TODO: unit-test
# TODO: doc
class Clients:
    _REGISTRY = {}
    _FOLLOWERS = defaultdict(set)
    _ALOCK = asyncio.Lock()

    @classmethod
    async def register(cls, client_id: str, writer: asyncio.StreamWriter):
        async with cls._ALOCK:
            cls._REGISTRY[int(client_id)] = writer

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
        async with cls._ALOCK:
            if client_id in cls._REGISTRY:
                cls._REGISTRY.pop(client_id)
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

        client_writer = maybe_client_writer
        client_writer.write(payload)

    @classmethod
    async def notify_all(cls, payload: bytes):
        async with cls._ALOCK:
            clients = list(cls._REGISTRY.keys())

        for client_id in clients:
            await cls.notify(client_id, payload)

    @classmethod
    async def notify_followers(cls, from_user_id: int, payload: bytes):
        async with cls._ALOCK:
            followers = list(cls._FOLLOWERS[from_user_id])

        if not followers:
            return

        for client_id in followers:
            await cls.notify(client_id, payload)
