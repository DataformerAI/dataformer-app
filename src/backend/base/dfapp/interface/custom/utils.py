import ast
import contextlib
import re
import traceback
import warnings
from typing import Any, Dict, List, Optional, Tuple, Union
from uuid import UUID

from fastapi import HTTPException
from loguru import logger
from pydantic import BaseModel

from dfapp.field_typing.range_spec import RangeSpec
from dfapp.interface.custom.attributes import ATTR_FUNC_MAPPING
from dfapp.interface.custom.code_parser.utils import extract_inner_type
from dfapp.interface.custom.custom_component import CustomComponent
from dfapp.interface.custom.directory_reader.utils import (
    build_custom_component_list_from_path,
    determine_component_name,
    merge_nested_dicts_with_renaming,
)
from dfapp.interface.custom.eval import eval_custom_component_code
from dfapp.interface.custom.schema import MissingDefault
from dfapp.schema import dotdict
from dfapp.template.field.base import TemplateField
from dfapp.template.frontend_node.custom_components import CustomComponentFrontendNode
from dfapp.utils import validate
from dfapp.utils.util import get_base_classes


class UpdateBuildConfigError(Exception):
    pass


def add_output_types(frontend_node: CustomComponentFrontendNode, return_types: List[str]):
    """Add output types to the frontend node"""
    for return_type in return_types:
        if return_type is None:
            raise HTTPException(
                status_code=400,
                detail={
                    "error": ("Invalid return type. Please check your code and try again."),
                    "traceback": traceback.format_exc(),
                },
            )
        if return_type == str:
            return_type = "Text"
        elif hasattr(return_type, "__name__"):
            return_type = return_type.__name__
        elif hasattr(return_type, "__class__"):
            return_type = return_type.__class__.__name__
        else:
            return_type = str(return_type)

        frontend_node.add_output_type(return_type)


def reorder_fields(frontend_node: CustomComponentFrontendNode, field_order: List[str]):
    """Reorder fields in the frontend node based on the specified field_order."""
    if not field_order:
        return

    # Create a dictionary for O(1) lookup time.
    field_dict = {field.name: field for field in frontend_node.template.fields}
    reordered_fields = [field_dict[name] for name in field_order if name in field_dict]
    # Add any fields that are not in the field_order list
    for field in frontend_node.template.fields:
        if field.name not in field_order:
            reordered_fields.append(field)
    frontend_node.template.fields = reordered_fields
    frontend_node.field_order = field_order


def add_base_classes(frontend_node: CustomComponentFrontendNode, return_types: List[str]):
    """Add base classes to the frontend node"""
    for return_type_instance in return_types:
        if return_type_instance is None:
            raise HTTPException(
                status_code=400,
                detail={
                    "error": ("Invalid return type. Please check your code and try again."),
                    "traceback": traceback.format_exc(),
                },
            )

        base_classes = get_base_classes(return_type_instance)
        if return_type_instance == str:
            base_classes.append("Text")

        for base_class in base_classes:
            frontend_node.add_base_class(base_class)


def extract_type_from_optional(field_type):
    """
    Extract the type from a string formatted as "Optional[<type>]".

    Parameters:
    field_type (str): The string from which to extract the type.

    Returns:
    str: The extracted type, or an empty string if no type was found.
    """
    match = re.search(r"\[(.*?)\]$", field_type)
    return match[1] if match else field_type


def get_field_properties(extra_field):
    """Get the properties of an extra field"""
    field_name = extra_field["name"]
    field_type = extra_field.get("type", "str")
    field_value = extra_field.get("default", "")
    # a required field is a field that does not contain
    # optional in field_type
    # and a field that does not have a default value
    field_required = "optional" not in field_type.lower() and isinstance(field_value, MissingDefault)
    field_value = field_value if not isinstance(field_value, MissingDefault) else None

    if not field_required:
        field_type = extract_type_from_optional(field_type)
    if field_value is not None:
        with contextlib.suppress(Exception):
            field_value = ast.literal_eval(field_value)
    return field_name, field_type, field_value, field_required


def process_type(field_type: str):
    if field_type.startswith("list") or field_type.startswith("List"):
        return extract_inner_type(field_type)

    # field_type is a string can be Prompt or Code too
    # so we just need to lower if it is the case
    lowercase_type = field_type.lower()
    if lowercase_type in ["prompt", "code"]:
        return lowercase_type
    return field_type


def add_new_custom_field(
    frontend_node: CustomComponentFrontendNode,
    field_name: str,
    field_type: str,
    field_value: Any,
    field_required: bool,
    field_config: dict,
):
    # Check field_config if any of the keys are in it
    # if it is, update the value
    display_name = field_config.pop("display_name", None)
    field_type = field_config.pop("field_type", field_type)
    field_contains_list = "list" in field_type.lower()
    field_type = process_type(field_type)
    field_value = field_config.pop("value", field_value)
    field_advanced = field_config.pop("advanced", False)

    if field_type == "Dict":
        field_type = "dict"

    if field_type == "bool" and field_value is None:
        field_value = False

    # If options is a list, then it's a dropdown
    # If options is None, then it's a list of strings
    is_list = isinstance(field_config.get("options"), list)
    field_config["is_list"] = is_list or field_config.get("list", False) or field_contains_list

    if "name" in field_config:
        warnings.warn("The 'name' key in field_config is used to build the object and can't be changed.")
    required = field_config.pop("required", field_required)
    placeholder = field_config.pop("placeholder", "")

    new_field = TemplateField(
        name=field_name,
        field_type=field_type,
        value=field_value,
        show=True,
        required=required,
        advanced=field_advanced,
        placeholder=placeholder,
        display_name=display_name,
        **sanitize_field_config(field_config),
    )
    frontend_node.template.upsert_field(field_name, new_field)
    if isinstance(frontend_node.custom_fields, dict):
        frontend_node.custom_fields[field_name] = None

    return frontend_node


def add_extra_fields(frontend_node, field_config, function_args):
    """Add extra fields to the frontend node"""
    if not function_args:
        return
    _field_config = field_config.copy()
    function_args_names = [arg["name"] for arg in function_args]
    # If kwargs is in the function_args and not all field_config keys are in function_args
    # then we need to add the extra fields

    for extra_field in function_args:
        if "name" not in extra_field or extra_field["name"] in [
            "self",
            "kwargs",
            "args",
        ]:
            continue

        field_name, field_type, field_value, field_required = get_field_properties(extra_field)
        config = _field_config.pop(field_name, {})
        frontend_node = add_new_custom_field(
            frontend_node,
            field_name,
            field_type,
            field_value,
            field_required,
            config,
        )
    if "kwargs" in function_args_names and not all(key in function_args_names for key in field_config.keys()):
        for field_name, field_config in _field_config.copy().items():
            if "name" not in field_config or field_name == "code":
                continue
            config = _field_config.get(field_name, {})
            config = config.model_dump() if isinstance(config, BaseModel) else config
            field_name, field_type, field_value, field_required = get_field_properties(extra_field=config)
            frontend_node = add_new_custom_field(
                frontend_node,
                field_name,
                field_type,
                field_value,
                field_required,
                config,
            )


def get_field_dict(field: Union[TemplateField, dict]):
    """Get the field dictionary from a TemplateField or a dict"""
    if isinstance(field, TemplateField):
        return dotdict(field.model_dump(by_alias=True, exclude_none=True))
    return field


def run_build_config(
    custom_component: CustomComponent,
    user_id: Optional[Union[str, UUID]] = None,
) -> Tuple[dict, CustomComponent]:
    """Build the field configuration for a custom component"""

    try:
        if custom_component.code is None:
            raise ValueError("Code is None")
        elif isinstance(custom_component.code, str):
            custom_class = eval_custom_component_code(custom_component.code)
        else:
            raise ValueError("Invalid code type")
    except Exception as exc:
        logger.error(f"Error while evaluating custom component code: {str(exc)}")
        raise HTTPException(
            status_code=400,
            detail={
                "error": ("Invalid type convertion. Please check your code and try again."),
                "traceback": traceback.format_exc(),
            },
        ) from exc

    try:
        custom_instance = custom_class(user_id=user_id)
        build_config: Dict = custom_instance.build_config()

        for field_name, field in build_config.copy().items():
            # Allow user to build TemplateField as well
            # as a dict with the same keys as TemplateField
            field_dict = get_field_dict(field)
            # Let's check if "rangeSpec" is a RangeSpec object
            if "rangeSpec" in field_dict and isinstance(field_dict["rangeSpec"], RangeSpec):
                field_dict["rangeSpec"] = field_dict["rangeSpec"].model_dump()
            build_config[field_name] = field_dict

        return build_config, custom_instance

    except Exception as exc:
        logger.error(f"Error while building field config: {str(exc)}")
        if hasattr(exc, "detail") and "traceback" in exc.detail:
            logger.error(exc.detail["traceback"])

        raise exc


def sanitize_template_config(template_config):
    """Sanitize the template config"""

    for key in template_config.copy():
        if key not in ATTR_FUNC_MAPPING.keys():
            template_config.pop(key, None)

    return template_config


def build_frontend_node(template_config):
    """Build a frontend node for a custom component"""
    try:
        sanitized_template_config = sanitize_template_config(template_config)
        return CustomComponentFrontendNode(**sanitized_template_config)
    except Exception as exc:
        logger.error(f"Error while building base frontend node: {exc}")
        raise exc


def add_code_field(frontend_node: CustomComponentFrontendNode, raw_code, field_config):
    code_field = TemplateField(
        dynamic=True,
        required=True,
        placeholder="",
        multiline=True,
        value=raw_code,
        password=False,
        name="code",
        advanced=True,
        field_type="code",
        is_list=False,
    )
    frontend_node.template.add_field(code_field)

    return frontend_node


def build_custom_component_template(
    custom_component: CustomComponent,
    user_id: Optional[Union[str, UUID]] = None,
) -> Tuple[Dict[str, Any], CustomComponent]:
    """Build a custom component template for the langchain"""
    try:
        frontend_node = build_frontend_node(custom_component.template_config)

        field_config, custom_instance = run_build_config(
            custom_component,
            user_id=user_id,
        )

        entrypoint_args = custom_component.get_function_entrypoint_args

        add_extra_fields(frontend_node, field_config, entrypoint_args)

        frontend_node = add_code_field(frontend_node, custom_component.code, field_config.get("code", {}))

        add_base_classes(frontend_node, custom_component.get_function_entrypoint_return_type)
        add_output_types(frontend_node, custom_component.get_function_entrypoint_return_type)

        reorder_fields(frontend_node, custom_instance._get_field_order())

        return frontend_node.to_dict(add_name=False), custom_instance
    except Exception as exc:
        if isinstance(exc, HTTPException):
            raise exc
        raise HTTPException(
            status_code=400,
            detail={
                "error": (f"Something went wrong while building the custom component. Hints: {str(exc)}"),
                "traceback": traceback.format_exc(),
            },
        ) from exc


def create_component_template(component):
    """Create a template for a component."""
    component_code = component["code"]
    component_output_types = component["output_types"]

    component_extractor = CustomComponent(code=component_code)

    component_template, _ = build_custom_component_template(component_extractor)
    if not component_template["output_types"] and component_output_types:
        component_template["output_types"] = component_output_types

    return component_template


def build_custom_components(components_paths: List[str]):
    """Build custom components from the specified paths."""
    if not components_paths:
        return {}

    logger.info(f"Building custom components from {components_paths}")
    custom_components_from_file: dict = {}
    processed_paths = set()
    for path in components_paths:
        path_str = str(path)
        if path_str in processed_paths:
            continue

        custom_component_dict = build_custom_component_list_from_path(path_str)
        if custom_component_dict:
            category = next(iter(custom_component_dict))
            logger.info(f"Loading {len(custom_component_dict[category])} component(s) from category {category}")
            custom_components_from_file = merge_nested_dicts_with_renaming(
                custom_components_from_file, custom_component_dict
            )
        processed_paths.add(path_str)

    return custom_components_from_file


def update_field_dict(
    custom_component_instance: "CustomComponent",
    field_dict: Dict,
    build_config: Dict,
    update_field: Optional[str] = None,
    update_field_value: Optional[Any] = None,
    call: bool = False,
):
    """Update the field dictionary by calling options() or value() if they are callable"""
    if ("real_time_refresh" in field_dict or "refresh_button" in field_dict) and any(
        (
            field_dict.get("real_time_refresh", False),
            field_dict.get("refresh_button", False),
        )
    ):
        if call:
            try:
                dd_build_config = dotdict(build_config)
                custom_component_instance.update_build_config(
                    build_config=dd_build_config,
                    field_value=update_field,
                    field_name=update_field_value,
                )
                build_config = dd_build_config
            except Exception as exc:
                logger.error(f"Error while running update_build_config: {str(exc)}")
                raise UpdateBuildConfigError(f"Error while running update_build_config: {str(exc)}") from exc

    return build_config


def sanitize_field_config(field_config: Union[Dict, TemplateField]):
    # If any of the already existing keys are in field_config, remove them
    if isinstance(field_config, TemplateField):
        field_dict = field_config.to_dict()
    else:
        field_dict = field_config
    for key in [
        "name",
        "field_type",
        "value",
        "required",
        "placeholder",
        "display_name",
        "advanced",
        "show",
    ]:
        field_dict.pop(key, None)
    return field_dict


def build_component(component):
    """Build a single component."""
    component_name = determine_component_name(component)
    component_template = create_component_template(component)

    return component_name, component_template


def get_function(code):
    """Get the function"""
    function_name = validate.extract_function_name(code)

    return validate.create_function(code, function_name)
