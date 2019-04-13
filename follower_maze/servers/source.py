import asyncio

from follower_maze import events


async def read_event(reader: asyncio.StreamReader) -> str:
    data = await reader.readline()
    return data.decode()


async def handle_source(reader: asyncio.StreamReader, writer: asyncio.StreamReader):
    while True:
        if events.buffer_is_full():
            await asyncio.sleep(1)
            continue

        event = await read_event(reader)

        # TODO: not sure about this, revisit later
        if not event:
            break

        # TODO: rm prints, add real handling
        print(events.handle(event))

        # TODO: remove sleep later
        await asyncio.sleep(1)


async def get_source_server(host: str, port: int) -> asyncio.AbstractServer:
    return await asyncio.start_server(handle_source, host, port)
