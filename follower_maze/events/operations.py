from follower_maze.events import parser
from follower_maze.events import handler


def parse(payload: bytes):
    return parser.EventParser(payload).parse()


async def handle(payload: bytes):
    event = parse(payload)
    await handler.EventHandler.new(event)


# TODO: implement smth like sliding window
def buffer_is_full() -> bool:
    return False
