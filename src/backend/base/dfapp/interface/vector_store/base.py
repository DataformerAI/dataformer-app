from typing import Any, Dict, List, Optional, Type

from langchain import vectorstores
from loguru import logger

from dfapp.interface.base import LangChainTypeCreator
from dfapp.interface.importing.utils import import_class
from dfapp.services.deps import get_settings_service
from dfapp.template.frontend_node.vectorstores import VectorStoreFrontendNode
from dfapp.utils.util import build_template_from_method


class VectorstoreCreator(LangChainTypeCreator):
    type_name: str = "vectorstores"

    @property
    def frontend_node_class(self) -> Type[VectorStoreFrontendNode]:
        return VectorStoreFrontendNode

    @property
    def type_to_loader_dict(self) -> Dict:
        if self.type_dict is None:
            self.type_dict: dict[str, Any] = {
                vectorstore_name: import_class(f"langchain_community.vectorstores.{vectorstore_name}")
                for vectorstore_name in vectorstores.__all__
            }
        return self.type_dict

    def get_signature(self, name: str) -> Optional[Dict]:
        """Get the signature of an embedding."""
        try:
            return build_template_from_method(
                name,
                type_to_cls_dict=self.type_to_loader_dict,
                method_name="from_texts",
            )
        except ValueError as exc:
            raise ValueError(f"Vector Store {name} not found") from exc
        except AttributeError as exc:
            logger.error(f"Vector Store {name} not loaded: {exc}")
            return None

    def to_list(self) -> List[str]:
        settings_service = get_settings_service()
        return [
            vectorstore
            for vectorstore in self.type_to_loader_dict.keys()
            if vectorstore in settings_service.settings.VECTORSTORES or settings_service.settings.DEV
        ]


vectorstore_creator = VectorstoreCreator()
