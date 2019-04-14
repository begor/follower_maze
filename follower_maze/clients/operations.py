import asyncio

from follower_maze.clients import registry


async def handle_new_client(client_id: str, writer: asyncio.StreamWriter):
    await registry.Clients.register(client_id=client_id, writer=writer)


async def follow(from_client: int, to_client: int, payload: bytes):
    await registry.Clients.follow(from_client_id=from_client, to_client_id=to_client)
    await registry.Clients.notify(client_id=to_client, payload=payload)


async def unfollow(from_client: int, to_client: int):
    await registry.Clients.unfollow(from_client_id=from_client, to_client_id=to_client)


async def broadcast(payload: bytes):
    await registry.Clients.notify_all(payload)


async def send_private_message(client_id: int, payload: bytes):
    await registry.Clients.notify(client_id=client_id, payload=payload)


# TODO: possibly rewrite
async def send_to_followers(client_id: int, payload: bytes):
    await registry.Clients.notify_followers(from_user_id=client_id, payload=payload)
