import asyncio

from follower_maze.clients import registry


async def handle_new_client(client_id: str, writer: asyncio.StreamWriter):
    await registry.Clients.register(client_id=client_id, writer=writer)
