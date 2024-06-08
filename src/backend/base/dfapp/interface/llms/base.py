from typing import Dict, List, Optional, Type

from loguru import logger

from dfapp.interface.base import LangChainTypeCreator
from dfapp.interface.custom_lists import llm_type_to_cls_dict
from dfapp.interface.utils import build_template_from_class
from dfapp.services.deps import get_settings_service
from dfapp.template.frontend_node.llms import LLMFrontendNode


class LLMCreator(LangChainTypeCreator):
    type_name: str = "models"

    @property
    def frontend_node_class(self) -> Type[LLMFrontendNode]:
        return LLMFrontendNode

    @property
    def type_to_loader_dict(self) -> Dict:
        if self.type_dict is None:
            self.type_dict = llm_type_to_cls_dict
        return self.type_dict

    def get_signature(self, name: str) -> Optional[Dict]:
        """Get the signature of an llm."""
        try:
            return build_template_from_class(name, llm_type_to_cls_dict)
        except ValueError as exc:
            raise ValueError("LLM not found") from exc

        except AttributeError as exc:
            logger.error(f"LLM {name} not loaded: {exc}")
            return None

    def to_list(self) -> List[str]:
        settings_service = get_settings_service()
        return [
            llm.__name__
            for llm in self.type_to_loader_dict.values()
            if llm.__name__ in settings_service.settings.LLMS or settings_service.settings.DEV
        ]


llm_creator = LLMCreator()
