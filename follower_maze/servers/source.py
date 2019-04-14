import asyncio

from follower_maze import events


async def handle_source(reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
    async for line in reader:
        # TODO: rm prints, add real handling
        await events.handle(line)


async def get_source_server(host: str, port: int) -> asyncio.AbstractServer:
    return await asyncio.start_server(handle_source, host, port)
