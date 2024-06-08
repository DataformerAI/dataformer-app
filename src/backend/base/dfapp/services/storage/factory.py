from loguru import logger

from dfapp.services.factory import ServiceFactory
from dfapp.services.session.service import SessionService
from dfapp.services.settings.service import SettingsService
from dfapp.services.storage.service import StorageService


class StorageServiceFactory(ServiceFactory):
    def __init__(self):
        super().__init__(
            StorageService,
        )

    def create(self, session_service: SessionService, settings_service: SettingsService):
        storage_type = settings_service.settings.STORAGE_TYPE
        if storage_type.lower() == "local":
            from .local import LocalStorageService

            return LocalStorageService(session_service, settings_service)
        elif storage_type.lower() == "s3":
            from .s3 import S3StorageService

            return S3StorageService(session_service, settings_service)
        else:
            logger.warning(f"Storage type {storage_type} not supported. Using local storage.")
            from .local import LocalStorageService

            return LocalStorageService(session_service, settings_service)
