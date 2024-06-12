import os

import yaml
from loguru import logger

from dfapp.services.base import Service
from dfapp.services.settings.auth import AuthSettings
from dfapp.services.settings.base import Settings


class SettingsService(Service):
    name = "settings_service"

    def __init__(self, settings: Settings, auth_settings: AuthSettings):
        super().__init__()
        self.settings = settings
        self.auth_settings = auth_settings

    @classmethod
    def load_settings_from_yaml(cls, file_path: str) -> "SettingsService":
        # Check if a string is a valid path or a file name
        if "/" not in file_path:
            # Get current path
            current_path = os.path.dirname(os.path.abspath(__file__))

            file_path = os.path.join(current_path, file_path)

        with open(file_path, "r") as f:
            settings_dict = yaml.safe_load(f)
            settings_dict = {k.upper(): v for k, v in settings_dict.items()}

            for key in settings_dict:
                if key not in Settings.model_fields.keys():
                    raise KeyError(f"Key {key} not found in settings")
                logger.debug(f"Loading {len(settings_dict[key])} {key} from {file_path}")

        settings = Settings(**settings_dict)
        if not settings.config_dir:
            raise ValueError("CONFIG_DIR must be set in settings")

        auth_settings = AuthSettings(
            CONFIG_DIR=settings.config_dir,
        )
        return cls(settings, auth_settings)
