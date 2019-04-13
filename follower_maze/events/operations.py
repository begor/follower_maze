from follower_maze.events import parser


def parse(event_data: str):
    return parser.EventParser(event_data).parse()


def handle(event_data: str):
    return parse(event_data)
