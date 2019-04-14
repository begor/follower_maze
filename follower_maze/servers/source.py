import asyncio

from follower_maze import events


async def read_event_payload(reader: asyncio.StreamReader) -> bytes:
    return await reader.readline()


async def handle_source(reader: asyncio.StreamReader, writer: asyncio.StreamReader):
    while True:
        if events.buffer_is_full():
            await asyncio.sleep(1)
            continue

        payload = await read_event_payload(reader)

        # TODO: not sure about this, revisit later
        if not payload:
            break

        # TODO: rm prints, add real handling
        await events.handle(payload)


async def get_source_server(host: str, port: int) -> asyncio.AbstractServer:
    return await asyncio.start_server(handle_source, host, port)
