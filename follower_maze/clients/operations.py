import asyncio
from typing import Optional

from follower_maze.clients import registry


async def handle_new_client(client_id: int, writer: asyncio.StreamWriter):
    """
        Register new client with `client_id` in `Clients` registry.

        NOTE: assumes `client_id` is globally unique.
    """
    await registry.Clients.register(client_id=client_id, writer=writer)


async def maybe_get_client_writer(client_id: int) -> Optional[asyncio.StreamWriter]:
    """
        Try to fetch `client_writer` from registry by `client_id`, checking two things:

        1) `client_id` is registered
        2) it's `client_writer` is not closed
    """
    return await registry.Clients.maybe_get_client_writer(client_id)


async def follow(from_client: int, to_client: int, payload: bytes):
    """
        Add follow relationship between two clients, notifying followed one (`to_client`).
    """
    await registry.Clients.follow(from_client_id=from_client, to_client_id=to_client)
    await registry.Clients.notify(client_id=to_client, payload=payload)


async def unfollow(from_client: int, to_client: int):
    """
        Silently removes follow relationship between two clients.
    """
    await registry.Clients.unfollow(from_client_id=from_client, to_client_id=to_client)


async def broadcast(payload: bytes):
    """
        Iterates over every registered and active client in registry, notifying every one of them with given `payload`.
    """
    await registry.Clients.notify_all(payload)


async def send_private_message(client_id: int, payload: bytes):
    """
        Notifying `client_id` with `payload` if it's in registry and not closed.
    """
    await registry.Clients.notify(client_id=client_id, payload=payload)


async def status_update(client_id: int, payload: bytes):
    """
        Notifying followers of `client_id` with `payload`.
    """
    await registry.Clients.notify_followers(from_user_id=client_id, payload=payload)
