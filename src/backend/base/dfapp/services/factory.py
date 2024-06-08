import importlib
import inspect
from typing import TYPE_CHECKING, Type, get_type_hints

from cachetools import LRUCache, cached
from loguru import logger

from dfapp.services.schema import ServiceType

if TYPE_CHECKING:
    from dfapp.services.base import Service


class ServiceFactory:
    def __init__(
        self,
        service_class,
    ):
        self.service_class = service_class
        self.dependencies = infer_service_types(self, import_all_services_into_a_dict())

    def create(self, *args, **kwargs) -> "Service":
        raise self.service_class(*args, **kwargs)


def hash_factory(factory: Type[ServiceFactory]) -> str:
    return factory.service_class.__name__


def hash_dict(d: dict) -> str:
    return str(d)


def hash_infer_service_types_args(factory_class: Type[ServiceFactory], available_services=None) -> str:
    factory_hash = hash_factory(factory_class)
    services_hash = hash_dict(available_services)
    return f"{factory_hash}_{services_hash}"


@cached(cache=LRUCache(maxsize=10), key=hash_infer_service_types_args)
def infer_service_types(factory_class: Type[ServiceFactory], available_services=None) -> list["ServiceType"]:
    create_method = factory_class.create
    type_hints = get_type_hints(create_method, globalns=available_services)
    service_types = []
    for param_name, param_type in type_hints.items():
        # Skip the return type if it's included in type hints
        if param_name == "return":
            continue

        # Convert the type to the expected enum format directly without appending "_SERVICE"
        type_name = param_type.__name__.upper().replace("SERVICE", "_SERVICE")

        try:
            # Attempt to find a matching enum value
            service_type = ServiceType[type_name]
            service_types.append(service_type)
        except KeyError:
            raise ValueError(f"No matching ServiceType for parameter type: {param_type.__name__}")
    return service_types


@cached(cache=LRUCache(maxsize=1))
def import_all_services_into_a_dict():
    # Services are all in dfapp.services.{service_name}.service
    # and are subclass of Service
    # We want to import all of them and put them in a dict
    # to use as globals
    from dfapp.services.base import Service

    services = {}
    for service_type in ServiceType:
        try:
            service_name = ServiceType(service_type).value.replace("_service", "")
            module_name = f"dfapp.services.{service_name}.service"
            module = importlib.import_module(module_name)
            for name, obj in inspect.getmembers(module, inspect.isclass):
                if issubclass(obj, Service) and obj is not Service:
                    services[name] = obj
                    break
        except Exception as exc:
            logger.exception(exc)
            raise RuntimeError("Could not initialize services. Please check your settings.") from exc
    return services
