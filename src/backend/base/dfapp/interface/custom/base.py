from typing import Any, Dict, List, Optional, Type

from loguru import logger

from dfapp.interface.base import LangChainTypeCreator

# from dfapp.interface.custom.custom import CustomComponent
from dfapp.custom import CustomComponent
from dfapp.template.frontend_node.custom_components import CustomComponentFrontendNode


class CustomComponentCreator(LangChainTypeCreator):
    type_name: str = "custom_components"

    @property
    def frontend_node_class(self) -> Type[CustomComponentFrontendNode]:
        return CustomComponentFrontendNode

    @property
    def type_to_loader_dict(self) -> Dict:
        if self.type_dict is None:
            self.type_dict: dict[str, Any] = {
                "CustomComponent": CustomComponent,
            }
        return self.type_dict

    def get_signature(self, name: str) -> Optional[Dict]:
        from dfapp.legacy_custom.customs import get_custom_nodes

        try:
            if name in get_custom_nodes(self.type_name).keys():
                return get_custom_nodes(self.type_name)[name]
        except ValueError as exc:
            raise ValueError(f"CustomComponent {name} not found: {exc}") from exc
        except AttributeError as exc:
            logger.error(f"CustomComponent {name} not loaded: {exc}")
            return None
        return None

    def to_list(self) -> List[str]:
        return list(self.type_to_loader_dict.keys())


custom_component_creator = CustomComponentCreator()
