from typing import Any, ClassVar, Dict, List, Optional, Type

from langchain_community import retrievers
from dfapp.interface.base import LangChainTypeCreator
from dfapp.interface.importing.utils import import_class
from dfapp.interface.utils import build_template_from_class
from dfapp.services.deps import get_settings_service
from dfapp.template.frontend_node.retrievers import RetrieverFrontendNode
from dfapp.utils.util import build_template_from_method
from loguru import logger


class RetrieverCreator(LangChainTypeCreator):
    type_name: str = "retrievers"

    from_method_nodes: ClassVar[Dict] = {
        "MultiQueryRetriever": "from_llm",
        "ZepRetriever": "__init__",
    }

    @property
    def frontend_node_class(self) -> Type[RetrieverFrontendNode]:
        return RetrieverFrontendNode

    @property
    def type_to_loader_dict(self) -> Dict:
        if self.type_dict is None:
            self.type_dict: dict[str, Any] = {
                retriever_name: import_class(f"langchain_community.retrievers.{retriever_name}")
                for retriever_name in retrievers.__all__
            }
        return self.type_dict

    def get_signature(self, name: str) -> Optional[Dict]:
        """Get the signature of an embedding."""
        try:
            if name in self.from_method_nodes:
                return build_template_from_method(
                    name,
                    type_to_cls_dict=self.type_to_loader_dict,
                    method_name=self.from_method_nodes[name],
                )
            else:
                return build_template_from_class(name, type_to_cls_dict=self.type_to_loader_dict)
        except ValueError as exc:
            raise ValueError(f"Retriever {name} not found") from exc
        except AttributeError as exc:
            logger.error(f"Retriever {name} not loaded: {exc}")
            return None

    def to_list(self) -> List[str]:
        settings_service = get_settings_service()
        return [
            retriever
            for retriever in self.type_to_loader_dict.keys()
            if retriever in settings_service.settings.RETRIEVERS or settings_service.settings.DEV
        ]


retriever_creator = RetrieverCreator()
