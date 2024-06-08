from typing import Optional

from loguru import logger

from dfapp.services.deps import get_settings_service
from dfapp.services.plugins.base import CallbackPlugin


class LangfuseInstance:
    _instance = None

    @classmethod
    def get(cls):
        logger.debug("Getting Langfuse instance")
        if cls._instance is None:
            cls.create()
        return cls._instance

    @classmethod
    def create(cls):
        try:
            logger.debug("Creating Langfuse instance")
            from langfuse import Langfuse  # type: ignore

            settings_manager = get_settings_service()

            if settings_manager.settings.LANGFUSE_PUBLIC_KEY and settings_manager.settings.LANGFUSE_SECRET_KEY:
                logger.debug("Langfuse credentials found")
                cls._instance = Langfuse(
                    public_key=settings_manager.settings.LANGFUSE_PUBLIC_KEY,
                    secret_key=settings_manager.settings.LANGFUSE_SECRET_KEY,
                    host=settings_manager.settings.LANGFUSE_HOST,
                )
            else:
                logger.debug("No Langfuse credentials found")
                cls._instance = None
        except ImportError:
            logger.debug("Langfuse not installed")
            cls._instance = None

    @classmethod
    def update(cls):
        logger.debug("Updating Langfuse instance")
        cls._instance = None
        cls.create()

    @classmethod
    def teardown(cls):
        logger.debug("Tearing down Langfuse instance")
        if cls._instance is not None:
            cls._instance.flush()
        cls._instance = None


class LangfusePlugin(CallbackPlugin):
    def initialize(self):
        LangfuseInstance.create()

    def teardown(self):
        LangfuseInstance.teardown()

    def get(self):
        return LangfuseInstance.get()

    def get_callback(self, _id: Optional[str] = None):
        if _id is None:
            _id = "default"

        logger.debug("Initializing langfuse callback")

        try:
            langfuse_instance = self.get()
            if langfuse_instance is not None and hasattr(langfuse_instance, "trace"):
                trace = langfuse_instance.trace(name="dfapp-" + _id, id=_id)
                if trace:
                    return trace.getNewHandler()

        except Exception as exc:
            logger.error(f"Error initializing langfuse callback: {exc}")

        return None
