from typing import TYPE_CHECKING

from dfapp.services.cache.service import AsyncInMemoryCache, CacheService, RedisCache, ThreadingInMemoryCache
from dfapp.services.factory import ServiceFactory
from dfapp.utils.logger import logger

if TYPE_CHECKING:
    from dfapp.services.settings.service import SettingsService


class CacheServiceFactory(ServiceFactory):
    def __init__(self):
        super().__init__(CacheService)

    def create(self, settings_service: "SettingsService"):
        # Here you would have logic to create and configure a CacheService
        # based on the settings_service

        if settings_service.settings.cache_type == "redis":
            logger.debug("Creating Redis cache")
            redis_cache = RedisCache(
                host=settings_service.settings.redis_host,
                port=settings_service.settings.redis_port,
                db=settings_service.settings.redis_db,
                url=settings_service.settings.redis_url,
                expiration_time=settings_service.settings.redis_cache_expire,
            )
            if redis_cache.is_connected():
                logger.debug("Redis cache is connected")
                return redis_cache
            logger.warning("Redis cache is not connected, falling back to in-memory cache")
            return ThreadingInMemoryCache()

        elif settings_service.settings.cache_type == "memory":
            return ThreadingInMemoryCache()
        elif settings_service.settings.cache_type == "async":
            return AsyncInMemoryCache()
