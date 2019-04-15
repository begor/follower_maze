import unittest

from follower_maze import clients
from follower_maze import events
from tests import factories
from tests import mocks
from tests.helpers import async_test

PAYLOAD1 = b"1"
PAYLOAD2 = b"2"

CLIENT1 = 1
CLIENT2 = 13
CLIENT3 = 87


class TestClientRegistry(unittest.TestCase):
    """
        Test ClientRegistry: correct mapping, notifies and auto-cleaning.
    """
    @async_test
    async def tearDown(self):
        await clients.registry.Clients.reset()

    @async_test
    async def test_register_one(self):
        client_id, client_writer = factories.get_client()

        await clients.handle_new_client(client_id=client_id, writer=client_writer)

        self.assertEqual(await clients.maybe_get_client_writer(client_id=client_id), client_writer)

    @async_test
    async def test_register_two(self):
        client_id1, client_writer1 = factories.get_client(CLIENT1)
        client_id2, client_writer2 = factories.get_client(CLIENT2)

        await clients.handle_new_client(client_id=client_id1, writer=client_writer1)
        await clients.handle_new_client(client_id=client_id2, writer=client_writer2)

        self.assertEqual(await clients.maybe_get_client_writer(client_id=client_id1), client_writer1)
        self.assertEqual(await clients.maybe_get_client_writer(client_id=client_id2), client_writer2)

    @async_test
    async def test_get_closed_writer(self):
        client_id, client_writer = factories.get_client()

        await clients.handle_new_client(client_id=client_id, writer=client_writer)

        self.assertEqual(await clients.maybe_get_client_writer(client_id=client_id), client_writer)

        client_writer.set_closing()

        self.assertIsNone(await clients.maybe_get_client_writer(client_id=client_id))

    @async_test
    async def test_broadcast_one_client(self):
        client_id, client_writer = factories.get_client()

        await clients.handle_new_client(client_id=client_id, writer=client_writer)
        await clients.broadcast(PAYLOAD1)

        self.assertEqual(len(client_writer.get_mailbox()), 1)
        self.assertIn(PAYLOAD1, client_writer.get_mailbox())

    @async_test
    async def test_broadcast_two_clients(self):
        client_id1, client_writer1 = factories.get_client(CLIENT1)
        client_id2, client_writer2 = factories.get_client(CLIENT2)

        await clients.handle_new_client(client_id=client_id1, writer=client_writer1)
        await clients.handle_new_client(client_id=client_id2, writer=client_writer2)
        await clients.broadcast(PAYLOAD1)

        self.assertEqual(len(client_writer1.get_mailbox()), 1)
        self.assertIn(PAYLOAD1, client_writer1.get_mailbox())

        self.assertEqual(len(client_writer2.get_mailbox()), 1)
        self.assertIn(PAYLOAD1, client_writer2.get_mailbox())

    @async_test
    async def test_broadcast_two_clients_one_closed(self):
        client_id1, client_writer1 = factories.get_client(CLIENT1)
        client_id2, client_writer2 = factories.get_client(CLIENT2)

        await clients.handle_new_client(client_id=client_id1, writer=client_writer1)
        await clients.handle_new_client(client_id=client_id2, writer=client_writer2)

        client_writer2.set_closing()

        await clients.broadcast(PAYLOAD1)

        self.assertEqual(len(client_writer1.get_mailbox()), 1)
        self.assertIn(PAYLOAD1, client_writer1.get_mailbox())

        self.assertEqual(len(client_writer2.get_mailbox()), 0)

    @async_test
    async def test_send_private_message_one_client(self):
        client_id, client_writer = factories.get_client()

        await clients.handle_new_client(client_id=client_id, writer=client_writer)
        await clients.send_private_message(client_id=client_id, payload=PAYLOAD1)

        self.assertEqual(len(client_writer.get_mailbox()), 1)
        self.assertIn(PAYLOAD1, client_writer.get_mailbox())

    @async_test
    async def test_send_private_message_different_client(self):
        client_id, client_writer = factories.get_client()

        await clients.handle_new_client(client_id=client_id, writer=client_writer)
        await clients.send_private_message(client_id=client_id + 1, payload=PAYLOAD1)

        self.assertEqual(len(client_writer.get_mailbox()), 0)

    @async_test
    async def test_follow(self):
        client_id1, client_writer1 = factories.get_client(CLIENT1)
        client_id2, client_writer2 = factories.get_client(CLIENT2)

        await clients.handle_new_client(client_id=client_id1, writer=client_writer1)
        await clients.handle_new_client(client_id=client_id2, writer=client_writer2)

        await clients.follow(from_client=client_id1, to_client=client_id2, payload=PAYLOAD1)

        self.assertEqual(len(client_writer1.get_mailbox()), 0)
        self.assertEqual(len(client_writer2.get_mailbox()), 1)
        self.assertIn(PAYLOAD1, client_writer2.get_mailbox())

    @async_test
    async def test_follow_closed(self):
        client_id1, client_writer1 = factories.get_client(CLIENT1)
        client_id2, client_writer2 = factories.get_client(CLIENT2)

        await clients.handle_new_client(client_id=client_id1, writer=client_writer1)
        await clients.handle_new_client(client_id=client_id2, writer=client_writer2)

        client_writer2.set_closing()

        await clients.follow(from_client=client_id1, to_client=client_id2, payload=PAYLOAD1)

        self.assertEqual(len(client_writer1.get_mailbox()), 0)
        self.assertEqual(len(client_writer2.get_mailbox()), 0)

    @async_test
    async def test_unfollow(self):
        client_id1, client_writer1 = factories.get_client(CLIENT1)
        client_id2, client_writer2 = factories.get_client(CLIENT2)

        await clients.handle_new_client(client_id=client_id1, writer=client_writer1)
        await clients.handle_new_client(client_id=client_id2, writer=client_writer2)

        await clients.unfollow(from_client=client_id1, to_client=client_id2)

        self.assertEqual(len(client_writer1.get_mailbox()), 0)
        self.assertEqual(len(client_writer2.get_mailbox()), 0)

    @async_test
    async def test_unfollow_closed(self):
        client_id1, client_writer1 = factories.get_client(CLIENT1)
        client_id2, client_writer2 = factories.get_client(CLIENT2)

        await clients.handle_new_client(client_id=client_id1, writer=client_writer1)
        await clients.handle_new_client(client_id=client_id2, writer=client_writer2)

        client_writer2.set_closing()

        await clients.unfollow(from_client=client_id1, to_client=client_id2)

        self.assertEqual(len(client_writer1.get_mailbox()), 0)
        self.assertEqual(len(client_writer2.get_mailbox()), 0)

    @async_test
    async def test_status_update_no_followers(self):
        client_id, client_writer = factories.get_client()

        await clients.handle_new_client(client_id=client_id, writer=client_writer)
        await clients.status_update(client_id=client_id, payload=PAYLOAD1)

        self.assertEqual(len(client_writer.get_mailbox()), 0)

    @async_test
    async def test_status_update_one_follower(self):
        client_id1, client_writer1 = factories.get_client(CLIENT1)
        client_id2, client_writer2 = factories.get_client(CLIENT2)

        await clients.handle_new_client(client_id=client_id1, writer=client_writer1)
        await clients.handle_new_client(client_id=client_id2, writer=client_writer2)

        await clients.follow(from_client=client_id2, to_client=client_id1, payload=PAYLOAD1)

        await clients.status_update(client_id=client_id1, payload=PAYLOAD2)

        self.assertEqual(len(client_writer1.get_mailbox()), 1)
        self.assertIn(PAYLOAD1, client_writer1.get_mailbox())

        self.assertEqual(len(client_writer2.get_mailbox()), 1)
        self.assertIn(PAYLOAD2, client_writer2.get_mailbox())

    @async_test
    async def test_status_update_two_followers(self):
        client_id1, client_writer1 = 1, mocks.MockClientWriter()
        client_id2, client_writer2 = 13, mocks.MockClientWriter()
        client_id3, client_writer3 = 17, mocks.MockClientWriter()

        await clients.handle_new_client(client_id=client_id1, writer=client_writer1)
        await clients.handle_new_client(client_id=client_id2, writer=client_writer2)
        await clients.handle_new_client(client_id=client_id3, writer=client_writer3)

        await clients.follow(from_client=client_id2, to_client=client_id1, payload=PAYLOAD1)
        await clients.follow(from_client=client_id3, to_client=client_id1, payload=PAYLOAD2)

        await clients.status_update(client_id=client_id1, payload=PAYLOAD2)

        self.assertEqual(len(client_writer1.get_mailbox()), 2)
        self.assertIn(PAYLOAD1, client_writer1.get_mailbox())
        self.assertEqual(len(client_writer2.get_mailbox()), 1)
        self.assertIn(PAYLOAD2, client_writer2.get_mailbox())
        self.assertEqual(len(client_writer3.get_mailbox()), 1)
        self.assertIn(PAYLOAD2, client_writer3.get_mailbox())

    @async_test
    async def test_status_update_two_followers_one_closed(self):
        client_id1, client_writer1 = factories.get_client(CLIENT1)
        client_id2, client_writer2 = factories.get_client(CLIENT2)
        client_id3, client_writer3 = factories.get_client(CLIENT3)

        await clients.handle_new_client(client_id=client_id1, writer=client_writer1)
        await clients.handle_new_client(client_id=client_id2, writer=client_writer2)
        await clients.handle_new_client(client_id=client_id3, writer=client_writer3)

        await clients.follow(from_client=client_id2, to_client=client_id1, payload=PAYLOAD1)
        await clients.follow(from_client=client_id3, to_client=client_id1, payload=PAYLOAD1)

        client_writer3.set_closing()

        await clients.status_update(client_id=client_id1, payload=PAYLOAD2)

        self.assertEqual(len(client_writer1.get_mailbox()), 2)
        self.assertIn(PAYLOAD1, client_writer1.get_mailbox())
        self.assertEqual(len(client_writer2.get_mailbox()), 1)
        self.assertIn(PAYLOAD2, client_writer2.get_mailbox())
        self.assertEqual(len(client_writer3.get_mailbox()), 0)

    @async_test
    async def test_no_status_update_after_unfollow(self):
        client_id1, client_writer1 = factories.get_client(CLIENT1)
        client_id2, client_writer2 = factories.get_client(CLIENT2)
        client_id3, client_writer3 = factories.get_client(CLIENT3)

        await clients.handle_new_client(client_id=client_id1, writer=client_writer1)
        await clients.handle_new_client(client_id=client_id2, writer=client_writer2)
        await clients.handle_new_client(client_id=client_id3, writer=client_writer3)

        await clients.follow(from_client=client_id2, to_client=client_id1, payload=PAYLOAD1)
        await clients.follow(from_client=client_id3, to_client=client_id1, payload=PAYLOAD1)
        await clients.unfollow(from_client=client_id3, to_client=client_id1)

        await clients.status_update(client_id=client_id1, payload=PAYLOAD2)

        self.assertEqual(len(client_writer1.get_mailbox()), 2)
        self.assertIn(PAYLOAD1, client_writer1.get_mailbox())
        self.assertEqual(len(client_writer2.get_mailbox()), 1)
        self.assertIn(PAYLOAD2, client_writer2.get_mailbox())
        self.assertEqual(len(client_writer3.get_mailbox()), 0)


if __name__ == '__main__':
    unittest.main()
