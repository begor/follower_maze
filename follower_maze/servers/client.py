import asyncio

from follower_maze import clients


async def parse_connection_msg(reader: asyncio.StreamReader) -> str:
    data = await reader.readline()
    return data.decode()


async def handle_client(reader, writer):
    client_id = await parse_connection_msg(reader)
    await clients.handle_new_client(client_id=client_id, writer=writer)


async def get_client_server(host: str, port: int) -> asyncio.AbstractServer:
    return await asyncio.start_server(handle_client, host, port)
