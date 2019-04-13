from dataclasses import dataclass

@dataclass
class Follow:
    seq_no: int
    from_user: str
    to_user: str


@dataclass
class Unfollow:
    seq_no: int
    from_user: str
    to_user: str


@dataclass
class Broadcast:
    seq_no: int


@dataclass
class PrivateMessage:
    seq_no: int
    from_user: str
    to_user: str


@dataclass
class StatusUpdate:
    seq_no: int
    from_user: str
