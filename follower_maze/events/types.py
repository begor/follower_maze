from dataclasses import dataclass


@dataclass
class Event:
    seq_no: int
    payload: bytes

    def __lt__(self, other):
        """
            Comparator to use Event in heap semantics.
        """
        return self.seq_no < other.seq_no


@dataclass
class Follow(Event):
    from_user: int
    to_user: int


@dataclass
class Unfollow(Event):
    from_user: int
    to_user: int


@dataclass
class Broadcast(Event):
    pass


@dataclass
class PrivateMessage(Event):
    from_user: int
    to_user: int


@dataclass
class StatusUpdate(Event):
    from_user: int
