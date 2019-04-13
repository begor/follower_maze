import asyncio
from typing import Optional


# TODO: unit-test
# TODO: doc
class ClientWriterRegistry:
    _REGISTRY = {}
    _ALOCK = asyncio.Lock()

    @classmethod
    async def register(cls, client_id: str, writer: asyncio.StreamWriter):
        async with cls._ALOCK:
            # TODO: not sure about this case, revisit later
            if client_id in cls._REGISTRY:
                raise RuntimeError(f'Client with id={client_id} already in Registry')

            cls._REGISTRY[client_id] = writer

    @classmethod
    async def maybe_get(cls, client_id: str) -> Optional[asyncio.StreamWriter]:
        async with cls._ALOCK:
            maybe_writer = cls._REGISTRY.get(client_id)

        if maybe_writer is None:
            return

        if maybe_writer.is_closing():
            await cls.delete(client_id)
            return

        return maybe_writer

    @classmethod
    async def delete(cls, client_id: str):
        async with cls._ALOCK:
            if client_id in cls._REGISTRY:
                cls._REGISTRY.pop(client_id)
