from follower_maze.events import parser
from follower_maze.events import handler


def parse(payload: bytes):
    """
        Parse given payload bytes into one of `types.Event` subclasses.
    """
    return parser.EventParser(payload).parse()


async def handle(payload: bytes):
    """
        Parse event and handle it using `EventHandler`.
    """
    event = parse(payload)
    await handler.EventHandler.new(event)
