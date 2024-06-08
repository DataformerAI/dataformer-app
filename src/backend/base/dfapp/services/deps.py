from contextlib import contextmanager
from typing import TYPE_CHECKING, Generator

from dfapp.services.schema import ServiceType

if TYPE_CHECKING:
    from sqlmodel import Session

    from dfapp.services.cache.service import CacheService
    from dfapp.services.chat.service import ChatService
    from dfapp.services.database.service import DatabaseService
    from dfapp.services.monitor.service import MonitorService
    from dfapp.services.plugins.service import PluginService
    from dfapp.services.session.service import SessionService
    from dfapp.services.settings.service import SettingsService
    from dfapp.services.socket.service import SocketIOService
    from dfapp.services.state.service import StateService
    from dfapp.services.storage.service import StorageService
    from dfapp.services.store.service import StoreService
    from dfapp.services.task.service import TaskService
    from dfapp.services.variable.service import VariableService


def get_service(service_type: ServiceType, default=None):
    """
    Retrieves the service instance for the given service type.

    Args:
        service_type (ServiceType): The type of service to retrieve.

    Returns:
        Any: The service instance.

    """
    from dfapp.services.manager import service_manager

    if not service_manager.factories:
        #! This is a workaround to ensure that the service manager is initialized
        #! Not optimal, but it works for now
        service_manager.register_factories()
    return service_manager.get(service_type, default)  # type: ignore


def get_state_service() -> "StateService":
    """
    Retrieves the StateService instance from the service manager.

    Returns:
        The StateService instance.
    """
    from dfapp.services.state.factory import StateServiceFactory

    return get_service(ServiceType.STATE_SERVICE, StateServiceFactory())  # type: ignore


def get_socket_service() -> "SocketIOService":
    """
    Get the SocketIOService instance from the service manager.

    Returns:
        SocketIOService: The SocketIOService instance.
    """
    return get_service(ServiceType.SOCKETIO_SERVICE)  # type: ignore


def get_storage_service() -> "StorageService":
    """
    Retrieves the storage service instance.

    Returns:
        The storage service instance.
    """
    from dfapp.services.storage.factory import StorageServiceFactory

    return get_service(ServiceType.STORAGE_SERVICE, default=StorageServiceFactory())  # type: ignore


def get_variable_service() -> "VariableService":
    """
    Retrieves the VariableService instance from the service manager.

    Returns:
        The VariableService instance.

    """
    from dfapp.services.variable.factory import VariableServiceFactory

    return get_service(ServiceType.VARIABLE_SERVICE, VariableServiceFactory())  # type: ignore


def get_plugins_service() -> "PluginService":
    """
    Get the PluginService instance from the service manager.

    Returns:
        PluginService: The PluginService instance.
    """
    return get_service(ServiceType.PLUGIN_SERVICE)  # type: ignore


def get_settings_service() -> "SettingsService":
    """
    Retrieves the SettingsService instance.

    If the service is not yet initialized, it will be initialized before returning.

    Returns:
        The SettingsService instance.

    Raises:
        ValueError: If the service cannot be retrieved or initialized.
    """
    from dfapp.services.settings.factory import SettingsServiceFactory

    return get_service(ServiceType.SETTINGS_SERVICE, SettingsServiceFactory())  # type: ignore


def get_db_service() -> "DatabaseService":
    """
    Retrieves the DatabaseService instance from the service manager.

    Returns:
        The DatabaseService instance.

    """
    from dfapp.services.database.factory import DatabaseServiceFactory

    return get_service(ServiceType.DATABASE_SERVICE, DatabaseServiceFactory())  # type: ignore


def get_session() -> Generator["Session", None, None]:
    """
    Retrieves a session from the database service.

    Yields:
        Session: A session object.

    """
    db_service = get_db_service()
    yield from db_service.get_session()


@contextmanager
def session_scope():
    """
    Context manager for managing a session scope.

    This context manager is used to manage a session scope for database operations.
    It ensures that the session is properly committed if no exceptions occur,
    and rolled back if an exception is raised.

    Yields:
        session: The session object.

    Raises:
        Exception: If an error occurs during the session scope.

    """
    session = next(get_session())
    try:
        yield session
        session.commit()
    except:
        session.rollback()
        raise
    finally:
        session.close()


def get_cache_service() -> "CacheService":
    """
    Retrieves the cache service from the service manager.

    Returns:
        The cache service instance.
    """
    from dfapp.services.cache.factory import CacheServiceFactory

    return get_service(ServiceType.CACHE_SERVICE, CacheServiceFactory())  # type: ignore


def get_session_service() -> "SessionService":
    """
    Retrieves the session service from the service manager.

    Returns:
        The session service instance.
    """
    from dfapp.services.session.factory import SessionServiceFactory

    return get_service(ServiceType.SESSION_SERVICE, SessionServiceFactory())  # type: ignore


def get_monitor_service() -> "MonitorService":
    """
    Retrieves the MonitorService instance from the service manager.

    Returns:
        MonitorService: The MonitorService instance.
    """
    from dfapp.services.monitor.factory import MonitorServiceFactory

    return get_service(ServiceType.MONITOR_SERVICE, MonitorServiceFactory())  # type: ignore


def get_task_service() -> "TaskService":
    """
    Retrieves the TaskService instance from the service manager.

    Returns:
        The TaskService instance.

    """
    from dfapp.services.task.factory import TaskServiceFactory

    return get_service(ServiceType.TASK_SERVICE, TaskServiceFactory())  # type: ignore


def get_chat_service() -> "ChatService":
    """
    Get the chat service instance.

    Returns:
        ChatService: The chat service instance.
    """
    return get_service(ServiceType.CHAT_SERVICE)  # type: ignore


def get_store_service() -> "StoreService":
    """
    Retrieves the StoreService instance from the service manager.

    Returns:
        StoreService: The StoreService instance.
    """
    return get_service(ServiceType.STORE_SERVICE)  # type: ignore
