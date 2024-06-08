from typing import ClassVar, Dict, List, Optional, Type

from dfapp.interface.base import LangChainTypeCreator
from dfapp.interface.custom_lists import memory_type_to_cls_dict
from dfapp.interface.utils import build_template_from_class
from dfapp.legacy_custom.customs import get_custom_nodes
from dfapp.services.deps import get_settings_service
from dfapp.template.frontend_node.base import FrontendNode
from dfapp.template.frontend_node.memories import MemoryFrontendNode
from dfapp.utils.util import build_template_from_method
from loguru import logger


class MemoryCreator(LangChainTypeCreator):
    type_name: str = "memories"

    from_method_nodes: ClassVar[Dict] = {
        "ZepChatMessageHistory": "__init__",
        "SQLiteEntityStore": "__init__",
    }

    @property
    def frontend_node_class(self) -> Type[FrontendNode]:
        """The class type of the FrontendNode created in frontend_node."""
        return MemoryFrontendNode

    @property
    def type_to_loader_dict(self) -> Dict:
        if self.type_dict is None:
            self.type_dict = memory_type_to_cls_dict
        return self.type_dict

    def get_signature(self, name: str) -> Optional[Dict]:
        """Get the signature of a memory."""
        try:
            if name in get_custom_nodes(self.type_name).keys():
                return get_custom_nodes(self.type_name)[name]
            elif name in self.from_method_nodes:
                return build_template_from_method(
                    name,
                    type_to_cls_dict=memory_type_to_cls_dict,
                    method_name=self.from_method_nodes[name],
                )
            return build_template_from_class(name, memory_type_to_cls_dict)
        except ValueError as exc:
            raise ValueError("Memory not found") from exc
        except AttributeError as exc:
            logger.error(f"Memory {name} not loaded: {exc}")
            return None

    def to_list(self) -> List[str]:
        settings_service = get_settings_service()
        return [
            memory.__name__
            for memory in self.type_to_loader_dict.values()
            if memory.__name__ in settings_service.settings.MEMORIES or settings_service.settings.DEV
        ]


memory_creator = MemoryCreator()
