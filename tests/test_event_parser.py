import unittest

from follower_maze import events


class TestEventParser(unittest.TestCase):
    PAYLOAD_TO_EXPECTED_EVENT = {
        b"42|B": events.types.Broadcast(seq_no=42, payload=b"42|B"),
        b"1|F|1|2": events.types.Follow(seq_no=1, from_user=1, to_user=2, payload=b"1|F|1|2"),
        b"101|P|11|17": events.types.PrivateMessage(seq_no=101, from_user=11, to_user=17, payload=b"101|P|11|17"),
        b"19|S|144": events.types.StatusUpdate(seq_no=19, from_user=144, payload=b"19|S|144"),
        b"5|U|9|13": events.types.Unfollow(seq_no=5, from_user=9, to_user=13, payload=b"5|U|9|13"),
    }

    def test_parse(self):
        for payload, expected_event in self.PAYLOAD_TO_EXPECTED_EVENT.items():
            self.assertEqual(events.parse(payload), expected_event)


if __name__ == '__main__':
    unittest.main()
