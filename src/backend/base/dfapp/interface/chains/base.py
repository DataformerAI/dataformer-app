from typing import Any, ClassVar, Dict, List, Optional, Type

from langchain import chains
from langchain_experimental.sql import SQLDatabaseChain
from dfapp.interface.base import LangChainTypeCreator
from dfapp.interface.importing.utils import import_class
from dfapp.interface.utils import build_template_from_class
from dfapp.legacy_custom.customs import get_custom_nodes
from dfapp.services.deps import get_settings_service
from dfapp.template.frontend_node.chains import ChainFrontendNode
from dfapp.utils.util import build_template_from_method
from loguru import logger

# Assuming necessary imports for Field, Template, and FrontendNode classes


class ChainCreator(LangChainTypeCreator):
    type_name: str = "chains"

    @property
    def frontend_node_class(self) -> Type[ChainFrontendNode]:
        return ChainFrontendNode

    #! We need to find a better solution for this
    from_method_nodes: ClassVar[Dict] = {
        "ConversationalRetrievalChain": "from_llm",
        "LLMCheckerChain": "from_llm",
        "SQLDatabaseChain": "from_llm",
    }

    @property
    def type_to_loader_dict(self) -> Dict:
        if self.type_dict is None:
            settings_service = get_settings_service()
            self.type_dict: dict[str, Any] = {
                chain_name: import_class(f"langchain.chains.{chain_name}") for chain_name in chains.__all__
            }
            from dfapp.interface.chains.custom import CUSTOM_CHAINS

            self.type_dict["SQLDatabaseChain"] = SQLDatabaseChain

            self.type_dict.update(CUSTOM_CHAINS)
            # Filter according to settings.chains
            self.type_dict = {
                name: chain
                for name, chain in self.type_dict.items()
                if name in settings_service.settings.CHAINS or settings_service.settings.DEV
            }
        return self.type_dict

    def get_signature(self, name: str) -> Optional[Dict]:
        try:
            if name in get_custom_nodes(self.type_name).keys():
                return get_custom_nodes(self.type_name)[name]
            elif name in self.from_method_nodes.keys():
                return build_template_from_method(
                    name,
                    type_to_cls_dict=self.type_to_loader_dict,
                    method_name=self.from_method_nodes[name],
                    add_function=True,
                )
            return build_template_from_class(name, self.type_to_loader_dict, add_function=True)
        except ValueError as exc:
            raise ValueError(f"Chain {name} not found: {exc}") from exc
        except AttributeError as exc:
            logger.error(f"Chain {name} not loaded: {exc}")
            return None

    def to_list(self) -> List[str]:
        names = []
        for _, chain in self.type_to_loader_dict.items():
            chain_name = chain.function_name() if hasattr(chain, "function_name") else chain.__name__
            names.append(chain_name)
        return names


chain_creator = ChainCreator()
