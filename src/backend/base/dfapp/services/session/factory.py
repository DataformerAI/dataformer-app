from typing import TYPE_CHECKING

from dfapp.services.factory import ServiceFactory
from dfapp.services.session.service import SessionService

if TYPE_CHECKING:
    from dfapp.services.cache.service import CacheService


class SessionServiceFactory(ServiceFactory):
    def __init__(self):
        super().__init__(SessionService)

    def create(self, cache_service: "CacheService"):
        return SessionService(cache_service)
