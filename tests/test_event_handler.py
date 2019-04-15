import unittest

from follower_maze import events
from tests import factories
from tests.helpers import async_test


class TestEventHandler(unittest.TestCase):
    """
        Test case for EventHandler.

        Mostly test correct ordering of events.
        Client notifies are tested in test_pipeline.
    """
    @async_test
    async def tearDown(self):
        await events.handler.EventHandler.reset()

    @async_test
    async def test_one_event_in_order(self):
        event = factories.get_broadcast_event(1)
        await events.handler.EventHandler.new(event)
        self.assertEqual(await events.handler.EventHandler.get_seq_no(), 1)

    @async_test
    async def test_two_events_in_order(self):
        first_event = factories.get_broadcast_event(1)
        await events.handler.EventHandler.new(first_event)

        self.assertEqual(await events.handler.EventHandler.get_seq_no(), 1)

        second_event = factories.get_broadcast_event(2)
        await events.handler.EventHandler.new(second_event)

        self.assertEqual(await events.handler.EventHandler.get_seq_no(), 2)

    @async_test
    async def test_one_event_out_order(self):
        event = factories.get_broadcast_event(2)
        await events.handler.EventHandler.new(event)
        self.assertEqual(await events.handler.EventHandler.get_seq_no(), 0)

    @async_test
    async def test_two_events_out_order(self):
        second_event = factories.get_broadcast_event(2)
        await events.handler.EventHandler.new(second_event)

        self.assertEqual(await events.handler.EventHandler.get_seq_no(), 0)

        first_event = factories.get_broadcast_event(3)
        await events.handler.EventHandler.new(first_event)

        self.assertEqual(await events.handler.EventHandler.get_seq_no(), 0)

    @async_test
    async def test_two_events_mixed_order(self):
        second_event = factories.get_broadcast_event(2)
        await events.handler.EventHandler.new(second_event)

        self.assertEqual(await events.handler.EventHandler.get_seq_no(), 0)

        first_event = factories.get_broadcast_event(1)
        await events.handler.EventHandler.new(first_event)
        self.assertEqual(await events.handler.EventHandler.get_seq_no(), 2)

    @async_test
    async def test_four_events_mixed_order(self):
        fourth_event = factories.get_broadcast_event(4)
        await events.handler.EventHandler.new(fourth_event)

        self.assertEqual(await events.handler.EventHandler.get_seq_no(), 0)

        second_event = factories.get_broadcast_event(2)
        await events.handler.EventHandler.new(second_event)

        self.assertEqual(await events.handler.EventHandler.get_seq_no(), 0)

        first_event = factories.get_broadcast_event(1)
        await events.handler.EventHandler.new(first_event)

        self.assertEqual(await events.handler.EventHandler.get_seq_no(), 2)

        third_event = factories.get_broadcast_event(3)
        await events.handler.EventHandler.new(third_event)

        self.assertEqual(await events.handler.EventHandler.get_seq_no(), 4)


if __name__ == '__main__':
    unittest.main()
