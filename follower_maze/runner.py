import asyncio

from follower_maze import servers

import logging

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")

    host, source_port, client_port = "127.0.0.1", 9090, 9099

    loop = asyncio.get_event_loop()

    source_server = loop.run_until_complete(servers.source.get_source_server(host=host, port=source_port))
    client_server = loop.run_until_complete(servers.client.get_client_server(host=host, port=client_port))

    logging.info(f"FollowerMaze started on host={host}, source_port={source_port}, client_port={client_port}")

    loop.run_until_complete(source_server.serve_forever())
    loop.run_until_complete(client_server.serve_forever())

