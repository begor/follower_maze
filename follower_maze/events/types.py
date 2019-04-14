from dataclasses import dataclass


@dataclass
class Event:
    seq_no: int
    payload: bytes

    def __lt__(self, other):
        return self.seq_no < other.seq_no


@dataclass
class Follow(Event):
    from_user: str
    to_user: str


@dataclass
class Unfollow(Event):
    from_user: str
    to_user: str


@dataclass
class Broadcast(Event):
    pass


@dataclass
class PrivateMessage(Event):
    from_user: str
    to_user: str


@dataclass
class StatusUpdate(Event):
    from_user: str
