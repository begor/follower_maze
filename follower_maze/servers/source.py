import asyncio


async def handle_source(reader, writer):
    while True:
        data = await reader.readline()
        message = data.decode()
        addr = writer.get_extra_info('peername')

        print(f"Received {message!r} from {addr!r}")


async def get_source_server(host: str, port: int) -> asyncio.AbstractServer:
    return await asyncio.start_server(handle_source, host, port)
