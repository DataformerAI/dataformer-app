from typing import Dict, List, Optional, Type

from langchain_community import utilities
from loguru import logger
from dfapp.interface.base import LangChainTypeCreator
from dfapp.interface.importing.utils import import_class
from dfapp.interface.utils import build_template_from_class
from dfapp.legacy_custom.customs import get_custom_nodes
from dfapp.services.deps import get_settings_service
from dfapp.template.frontend_node.utilities import UtilitiesFrontendNode


class UtilityCreator(LangChainTypeCreator):
    type_name: str = "utilities"

    @property
    def frontend_node_class(self) -> Type[UtilitiesFrontendNode]:
        return UtilitiesFrontendNode

    @property
    def type_to_loader_dict(self) -> Dict:
        """
        Returns a dictionary mapping utility names to their corresponding loader classes.
        If the dictionary has not been created yet, it is created by importing all utility classes
        from the langchain.chains module and filtering them according to the settings.utilities list.
        """
        if self.type_dict is None:
            settings_service = get_settings_service()
            self.type_dict = {}
            for utility_name in utilities.__all__:
                try:
                    imported = import_class(f"langchain_community.utilities.{utility_name}")
                    self.type_dict[utility_name] = imported
                except Exception:
                    pass

            self.type_dict["SQLDatabase"] = utilities.SQLDatabase
            # Filter according to settings.utilities
            self.type_dict = {
                name: utility
                for name, utility in self.type_dict.items()
                if name in settings_service.settings.UTILITIES or settings_service.settings.DEV
            }

        return self.type_dict

    def get_signature(self, name: str) -> Optional[Dict]:
        """Get the signature of a utility."""
        try:
            custom_nodes = get_custom_nodes(self.type_name)
            if name in custom_nodes.keys():
                return custom_nodes[name]
            return build_template_from_class(name, self.type_to_loader_dict)
        except ValueError as exc:
            raise ValueError(f"Utility {name} not found") from exc

        except AttributeError as exc:
            logger.error(f"Utility {name} not loaded: {exc}")
            return None

    def to_list(self) -> List[str]:
        return list(self.type_to_loader_dict.keys())


utility_creator = UtilityCreator()
