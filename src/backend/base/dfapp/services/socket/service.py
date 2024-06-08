from typing import TYPE_CHECKING, Any

import socketio  # type: ignore
from loguru import logger

from dfapp.services.base import Service
from dfapp.services.deps import get_chat_service
from dfapp.services.socket.utils import build_vertex, get_vertices

if TYPE_CHECKING:
    from dfapp.services.cache.service import CacheService


class SocketIOService(Service):
    name = "socket_service"

    def __init__(self, cache_service: "CacheService"):
        self.cache_service = cache_service

    def init(self, sio: socketio.AsyncServer):
        # Registering event handlers
        self.sio = sio
        if self.sio:
            self.sio.event(self.connect)
            self.sio.event(self.disconnect)
            self.sio.on("message")(self.message)
            self.sio.on("get_vertices")(self.on_get_vertices)
            self.sio.on("build_vertex")(self.on_build_vertex)
        self.sessions = {}  # type: dict[str, dict]

    async def emit_error(self, sid, error):
        await self.sio.emit("error", to=sid, data=error)

    async def connect(self, sid, environ):
        logger.info(f"Socket connected: {sid}")
        self.sessions[sid] = environ

    async def disconnect(self, sid):
        logger.info(f"Socket disconnected: {sid}")
        self.sessions.pop(sid, None)

    async def message(self, sid, data=None):
        # Logic for handling messages
        await self.emit_message(to=sid, data=data or {"foo": "bar", "baz": [1, 2, 3]})

    async def emit_message(self, to, data):
        # Abstracting sio.emit
        await self.sio.emit("message", to=to, data=data)

    async def emit_token(self, to, data):
        await self.sio.emit("token", to=to, data=data)

    async def on_get_vertices(self, sid, flow_id):
        await get_vertices(self.sio, sid, flow_id, get_chat_service())

    async def on_build_vertex(self, sid, flow_id, vertex_id, tweaks, inputs):
        await build_vertex(
            sio=self.sio,
            sid=sid,
            flow_id=flow_id,
            vertex_id=vertex_id,
            tweaks=tweaks,
            inputs=inputs,
            get_cache=self.get_cache,
            set_cache=self.set_cache,
        )

    def get_cache(self, sid: str) -> Any:
        """
        Get the cache for a client.
        """
        return self.cache_service.get(sid)

    def set_cache(self, sid: str, build_result: Any) -> bool:
        """
        Set the cache for a client.
        """
        # client_id is the flow id but that already exists in the cache
        # so we need to change it to something else

        result_dict = {
            "result": build_result,
            "type": type(build_result),
        }
        self.cache_service.upsert(sid, result_dict)
        return sid in self.cache_service
