from typing import Dict, List, Optional

from langchain_community.utilities import requests
from dfapp.interface.base import LangChainTypeCreator
from dfapp.interface.utils import build_template_from_class
from loguru import logger


class WrapperCreator(LangChainTypeCreator):
    type_name: str = "wrappers"

    @property
    def type_to_loader_dict(self) -> Dict:
        if self.type_dict is None:
            self.type_dict = {wrapper.__name__: wrapper for wrapper in [requests.TextRequestsWrapper]}
        return self.type_dict

    def get_signature(self, name: str) -> Optional[Dict]:
        try:
            return build_template_from_class(name, self.type_to_loader_dict)
        except ValueError as exc:
            raise ValueError("Wrapper not found") from exc
        except AttributeError as exc:
            logger.error(f"Wrapper {name} not loaded: {exc}")
            return None

    def to_list(self) -> List[str]:
        return list(self.type_to_loader_dict.keys())


wrapper_creator = WrapperCreator()
