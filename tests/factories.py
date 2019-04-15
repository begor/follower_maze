import random

from follower_maze import events
from tests import mocks


def get_client(client_id=None):
    return client_id or random.randint(0, 100), mocks.MockClientWriter()


def get_broadcast_event(seq_no: int):
    return events.types.Broadcast(seq_no=seq_no, payload=f"{seq_no}|B")
