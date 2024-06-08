from typing import TYPE_CHECKING

from dfapp.services.factory import ServiceFactory
from dfapp.services.store.service import StoreService

if TYPE_CHECKING:
    from dfapp.services.settings.service import SettingsService


class StoreServiceFactory(ServiceFactory):
    def __init__(self):
        super().__init__(StoreService)

    def create(self, settings_service: "SettingsService"):
        return StoreService(settings_service)
