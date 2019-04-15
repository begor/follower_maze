import asyncio

from follower_maze import clients


async def parse_connection_msg(reader: asyncio.StreamReader) -> str:
    data = await reader.readline()
    return data.decode()


async def handle_client(reader, writer):
    """
        Handle for client connections.

        Just parse one message with client id, decode it and register this client via `clients.handle_new_client`.
    """
    client_id = await parse_connection_msg(reader)
    await clients.handle_new_client(client_id=int(client_id), writer=writer)


async def get_client_server(host: str, port: int) -> asyncio.AbstractServer:
    return await asyncio.start_server(handle_client, host, port)
