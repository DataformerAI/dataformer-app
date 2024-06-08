import asyncio
from collections import defaultdict
from typing import Any, Optional

from dfapp.services.base import Service
from dfapp.services.deps import get_cache_service


class ChatService(Service):
    name = "chat_service"

    def __init__(self):
        self._cache_locks = defaultdict(asyncio.Lock)
        self.cache_service = get_cache_service()

    async def set_cache(self, flow_id: str, data: Any, lock: Optional[asyncio.Lock] = None) -> bool:
        """
        Set the cache for a client.
        """
        # client_id is the flow id but that already exists in the cache
        # so we need to change it to something else
        result_dict = {
            "result": data,
            "type": type(data),
        }
        await self.cache_service.upsert(flow_id, result_dict, lock=lock or self._cache_locks[flow_id])
        return flow_id in self.cache_service

    async def get_cache(self, flow_id: str, lock: Optional[asyncio.Lock] = None) -> Any:
        """
        Get the cache for a client.
        """
        return await self.cache_service.get(flow_id, lock=lock or self._cache_locks[flow_id])

    async def clear_cache(self, flow_id: str, lock: Optional[asyncio.Lock] = None):
        """
        Clear the cache for a client.
        """
        await self.cache_service.delete(flow_id, lock=lock or self._cache_locks[flow_id])
