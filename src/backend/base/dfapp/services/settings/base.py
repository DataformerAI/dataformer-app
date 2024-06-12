import contextlib
import json
import os
from pathlib import Path
from shutil import copy2
from typing import Any, List, Optional, Tuple, Type

import orjson
import yaml
from loguru import logger
from pydantic import field_validator
from pydantic.fields import FieldInfo
from pydantic_settings import BaseSettings, EnvSettingsSource, PydanticBaseSettingsSource, SettingsConfigDict

from dfapp.services.settings.constants import VARIABLES_TO_GET_FROM_ENVIRONMENT

# BASE_COMPONENTS_PATH = str(Path(__file__).parent / "components")
BASE_COMPONENTS_PATH = str(Path(__file__).parent.parent.parent / "components")


def is_list_of_any(field: FieldInfo) -> bool:
    """
    Check if the given field is a list or an optional list of any type.

    Args:
        field (FieldInfo): The field to be checked.

    Returns:
        bool: True if the field is a list or a list of any type, False otherwise.
    """
    if field.annotation is None:
        return False
    try:
        if hasattr(field.annotation, "__args__"):
            union_args = field.annotation.__args__
        else:
            union_args = []

        return field.annotation.__origin__ == list or any(
            arg.__origin__ == list for arg in union_args if hasattr(arg, "__origin__")
        )
    except AttributeError:
        return False


class MyCustomSource(EnvSettingsSource):
    def prepare_field_value(self, field_name: str, field: FieldInfo, value: Any, value_is_complex: bool) -> Any:
        # allow comma-separated list parsing

        # fieldInfo contains the annotation of the field
        if is_list_of_any(field):
            if isinstance(value, str):
                value = value.split(",")
            if isinstance(value, list):
                return value

        return super().prepare_field_value(field_name, field, value, value_is_complex)


class Settings(BaseSettings):
    # Define the default DFAPP_DIR
    config_dir: Optional[str] = None
    # Define if dfapp db should be saved in config dir or
    # in the dfapp directory
    save_db_in_config_dir: bool = False
    """Define if dfapp database should be saved in DFAPP_CONFIG_DIR or in the dfapp directory (i.e. in the package directory)."""

    dev: bool = False
    database_url: Optional[str] = None
    """Database URL for DataformerApp. If not provided, DataformerApp will use a SQLite database."""
    pool_size: int = 10
    """The number of connections to keep open in the connection pool. If not provided, the default is 10."""
    max_overflow: int = 20
    """The number of connections to allow that can be opened beyond the pool size. If not provided, the default is 10."""
    cache_type: str = "async"
    remove_api_keys: bool = False
    components_path: List[str] = []
    langchain_cache: str = "InMemoryCache"
    load_flows_path: Optional[str] = None

    # Redis
    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_db: int = 0
    redis_url: Optional[str] = None
    redis_cache_expire: int = 3600

    # PLUGIN_DIR: Optional[str] = None

    langfuse_secret_key: Optional[str] = None
    langfuse_public_key: Optional[str] = None
    langfuse_host: Optional[str] = None

    store: Optional[bool] = True
    store_url: Optional[str] = "https://api.dataformer.store"
    download_webhook_url: Optional[str] = (
        "https://api.dataformer.store/flows/trigger/ec611a61-8460-4438-b187-a4f65e5559d4"
    )
    like_webhook_url: Optional[str] = "https://api.dataformer.store/flows/trigger/64275852-ec00-45c1-984e-3bff814732da"

    storage_type: str = "local"

    celery_enabled: bool = False

    fallback_to_env_var: bool = True
    """If set to True, Global Variables set in the UI will fallback to a environment variable
    with the same name in case DataformerApp fails to retrieve the variable value."""

    store_environment_variables: bool = True
    """Whether to store environment variables as Global Variables in the database."""
    variables_to_get_from_environment: list[str] = VARIABLES_TO_GET_FROM_ENVIRONMENT
    """List of environment variables to get from the environment and store in the database."""
    worker_timeout: int = 300
    """Timeout for the API calls in seconds."""
    frontend_timeout: int = 0
    """Timeout for the frontend API calls in seconds."""

    @field_validator("config_dir", mode="before")
    def set_dfapp_dir(cls, value):
        if not value:
            from platformdirs import user_cache_dir

            # Define the app name and author
            app_name = "dfapp"
            app_author = "dfapp"

            # Get the cache directory for the application
            cache_dir = user_cache_dir(app_name, app_author)

            # Create a .dfapp directory inside the cache directory
            value = Path(cache_dir)
            value.mkdir(parents=True, exist_ok=True)

        if isinstance(value, str):
            value = Path(value)
        if not value.exists():
            value.mkdir(parents=True, exist_ok=True)

        return str(value)

    @field_validator("database_url", mode="before")
    def set_database_url(cls, value, info):
        if not value:
            logger.debug("No database_url provided, trying DFAPP_DATABASE_URL env variable")
            if dfapp_database_url := os.getenv("DFAPP_DATABASE_URL"):
                value = dfapp_database_url
                logger.debug("Using DFAPP_DATABASE_URL env variable.")
            else:
                logger.debug("No database_url env variable, using sqlite database")
                # Originally, we used sqlite:///./dfapp.db
                # so we need to migrate to the new format
                # if there is a database in that location
                if not info.data["config_dir"]:
                    raise ValueError("config_dir not set, please set it or provide a database_url")
                try:
                    from dfapp.version import is_pre_release  # type: ignore
                except ImportError:
                    from importlib import metadata

                    version = metadata.version("dfapp-base")
                    is_pre_release = "a" in version or "b" in version or "rc" in version

                if info.data["save_db_in_config_dir"]:
                    database_dir = info.data["config_dir"]
                    logger.debug(f"Saving database to config_dir: {database_dir}")
                else:
                    database_dir = Path(__file__).parent.parent.parent.resolve()
                    logger.debug(f"Saving database to dfapp directory: {database_dir}")

                pre_db_file_name = "dfapp-pre.db"
                db_file_name = "dfapp.db"
                new_pre_path = f"{database_dir}/{pre_db_file_name}"
                new_path = f"{database_dir}/{db_file_name}"
                final_path = None
                if is_pre_release:
                    if Path(new_pre_path).exists():
                        final_path = new_pre_path
                    elif Path(new_path).exists() and info.data["save_db_in_config_dir"]:
                        # We need to copy the current db to the new location
                        logger.debug("Copying existing database to new location")
                        copy2(new_path, new_pre_path)
                        logger.debug(f"Copied existing database to {new_pre_path}")
                    elif Path(f"./{db_file_name}").exists() and info.data["save_db_in_config_dir"]:
                        logger.debug("Copying existing database to new location")
                        copy2(f"./{db_file_name}", new_pre_path)
                        logger.debug(f"Copied existing database to {new_pre_path}")
                    else:
                        logger.debug(f"Creating new database at {new_pre_path}")
                        final_path = new_pre_path
                else:
                    if Path(new_path).exists():
                        logger.debug(f"Database already exists at {new_path}, using it")
                        final_path = new_path
                    elif Path("./{db_file_name}").exists():
                        try:
                            logger.debug("Copying existing database to new location")
                            copy2("./{db_file_name}", new_path)
                            logger.debug(f"Copied existing database to {new_path}")
                        except Exception:
                            logger.error("Failed to copy database, using default path")
                            new_path = "./{db_file_name}"
                    else:
                        final_path = new_path

                if final_path is None:
                    if is_pre_release:
                        final_path = new_pre_path
                    else:
                        final_path = new_path

                value = f"sqlite:///{final_path}"

        return value

    @field_validator("components_path", mode="before")
    def set_components_path(cls, value):
        if os.getenv("DFAPP_COMPONENTS_PATH"):
            logger.debug("Adding DFAPP_COMPONENTS_PATH to components_path")
            dfapp_component_path = os.getenv("DFAPP_COMPONENTS_PATH")
            if Path(dfapp_component_path).exists() and dfapp_component_path not in value:
                if isinstance(dfapp_component_path, list):
                    for path in dfapp_component_path:
                        if path not in value:
                            value.append(path)
                    logger.debug(f"Extending {dfapp_component_path} to components_path")
                elif dfapp_component_path not in value:
                    value.append(dfapp_component_path)
                    logger.debug(f"Appending {dfapp_component_path} to components_path")

        if not value:
            value = [BASE_COMPONENTS_PATH]
            logger.debug("Setting default components path to components_path")
        elif BASE_COMPONENTS_PATH not in value:
            value.append(BASE_COMPONENTS_PATH)
            logger.debug("Adding default components path to components_path")

        logger.debug(f"Components path: {value}")
        return value

    model_config = SettingsConfigDict(validate_assignment=True, extra="ignore", env_prefix="DFAPP_")

    def update_from_yaml(self, file_path: str, dev: bool = False):
        new_settings = load_settings_from_yaml(file_path)
        self.components_path = new_settings.components_path or []
        self.dev = dev

    def update_settings(self, **kwargs):
        logger.debug("Updating settings")
        for key, value in kwargs.items():
            # value may contain sensitive information, so we don't want to log it
            if not hasattr(self, key):
                logger.debug(f"Key {key} not found in settings")
                continue
            logger.debug(f"Updating {key}")
            if isinstance(getattr(self, key), list):
                # value might be a '[something]' string
                with contextlib.suppress(json.decoder.JSONDecodeError):
                    value = orjson.loads(str(value))
                if isinstance(value, list):
                    for item in value:
                        if isinstance(item, Path):
                            item = str(item)
                        if item not in getattr(self, key):
                            getattr(self, key).append(item)
                    logger.debug(f"Extended {key}")
                else:
                    if isinstance(value, Path):
                        value = str(value)
                    if value not in getattr(self, key):
                        getattr(self, key).append(value)
                        logger.debug(f"Appended {key}")

            else:
                setattr(self, key, value)
                logger.debug(f"Updated {key}")
            logger.debug(f"{key}: {getattr(self, key)}")

    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls: Type[BaseSettings],
        init_settings: PydanticBaseSettingsSource,
        env_settings: PydanticBaseSettingsSource,
        dotenv_settings: PydanticBaseSettingsSource,
        file_secret_settings: PydanticBaseSettingsSource,
    ) -> Tuple[PydanticBaseSettingsSource, ...]:
        return (MyCustomSource(settings_cls),)


def save_settings_to_yaml(settings: Settings, file_path: str):
    with open(file_path, "w") as f:
        settings_dict = settings.model_dump()
        yaml.dump(settings_dict, f)


def load_settings_from_yaml(file_path: str) -> Settings:
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

    return Settings(**settings_dict)
