import asyncio

from follower_maze import events


async def handle_source(reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
    """
        Handle for source connection.

        Just read events from source line by line and handle them via `events.handle` action
    """
    async for line in reader:
        await events.handle(line)


async def get_source_server(host: str, port: int) -> asyncio.AbstractServer:
    return await asyncio.start_server(handle_source, host, port)
