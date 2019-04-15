class MockClientWriter:
    """
        Object that acts similar to asyncio.StreamWriter and used for client notifying tests.
    """
    def __init__(self):
        self._is_closing = False
        self._mailbox = []

    def set_closing(self):
        self._is_closing = True

    def is_closing(self):
        return self._is_closing

    def write(self, message):
        self._mailbox.append(message)

    def get_mailbox(self):
        return self._mailbox
