from typing import Tuple

from follower_maze.events import types


class EventParser:
    """
        Parses given bytes payload into one of `types.Event` subclasses.

        NOTE: it assumes correct event type and will fail fast for unknown event.
    """
    def __init__(self, payload: bytes, delimiter: str = "|"):
        self._payload = payload
        self._event_data = payload.decode()
        self._delimiter = delimiter

    def parse(self):
        seq_no, event_type, destinations = self._tokenize()
        parser = self._get_type_parser(event_type)

        return parser(seq_no, *destinations)

    def _tokenize(self) -> Tuple[int, str, tuple]:
        seq_no, event_type, *destinations = self._event_data.split(self._delimiter)
        return int(seq_no), event_type[0], tuple(int(dest) for dest in destinations)

    def _get_type_parser(self, event_type: str):
        parsers = {
            "B": self._parse_broadcast,
            "F": self._parse_follow,
            "P": self._parse_private,
            "S": self._parse_status,
            "U": self._parse_unfollow,
        }

        return parsers[event_type]

    def _parse_broadcast(self, seq_no: int, *_) -> types.Broadcast:
        return types.Broadcast(seq_no=seq_no, payload=self._payload)

    def _parse_follow(self, seq_no: int, from_user: str, to_user: str) -> types.Follow:
        return types.Follow(seq_no=seq_no, payload=self._payload, from_user=from_user, to_user=to_user)

    def _parse_private(self, seq_no: int, from_user: str, to_user: str) -> types.PrivateMessage:
        return types.PrivateMessage(seq_no=seq_no, payload=self._payload, from_user=from_user, to_user=to_user)

    def _parse_status(self, seq_no: int, from_user: str, *_) -> types.StatusUpdate:
        return types.StatusUpdate(seq_no=seq_no, payload=self._payload, from_user=from_user)

    def _parse_unfollow(self, seq_no: int, from_user: str, to_user: str) -> types.Unfollow:
        return types.Unfollow(seq_no=seq_no, payload=self._payload, from_user=from_user, to_user=to_user)
