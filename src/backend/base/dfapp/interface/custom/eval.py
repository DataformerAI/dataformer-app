from typing import TYPE_CHECKING, Type

from dfapp.utils import validate

if TYPE_CHECKING:
    from dfapp.interface.custom.custom_component import CustomComponent


def eval_custom_component_code(code: str) -> Type["CustomComponent"]:
    """Evaluate custom component code"""
    class_name = validate.extract_class_name(code)
    return validate.create_class(code, class_name)
