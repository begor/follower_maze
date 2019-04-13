import asyncio


async def handle_source(reader, writer):
    while True:
        data = await reader.readline()
        message = data.decode()
        addr = writer.get_extra_info('peername')

        print(f"Received {message!r} from {addr!r}")


async def handle_client(reader, writer):
    data = await reader.readline()
    message = data.decode()
    addr = writer.get_extra_info('peername')

    print(f"Client {message} connected from {addr}")


async def get_source_server():
    return await asyncio.start_server(
        handle_source, '127.0.0.1', 9090)


async def get_client_server():
    return await asyncio.start_server(
        handle_client, '127.0.0.1', 9099)


loop = asyncio.get_event_loop()

source_server = loop.run_until_complete(get_source_server())
client_server = loop.run_until_complete(get_client_server())

loop.run_until_complete(source_server.serve_forever())
loop.run_until_complete(client_server.serve_forever())
