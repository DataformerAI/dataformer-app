import base64
import json
import os
import re
from io import BytesIO
from typing import Dict

import yaml
from docstring_parser import parse
from langchain.base_language import BaseLanguageModel
from dfapp.services.chat.config import ChatConfig
from dfapp.services.deps import get_settings_service
from dfapp.utils.util import format_dict, get_base_classes, get_default_factory
from loguru import logger
from PIL.Image import Image


def load_file_into_dict(file_path: str) -> dict:
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")

    # Files names are UUID, so we can't find the extension
    with open(file_path, "r") as file:
        try:
            data = json.load(file)
        except json.JSONDecodeError:
            file.seek(0)
            data = yaml.safe_load(file)
        except ValueError as exc:
            raise ValueError("Invalid file type. Expected .json or .yaml.") from exc
    return data


def pil_to_base64(image: Image) -> str:
    buffered = BytesIO()
    image.save(buffered, format="PNG")
    img_str = base64.b64encode(buffered.getvalue())
    return img_str.decode("utf-8")


def try_setting_streaming_options(langchain_object):
    # If the LLM type is OpenAI or ChatOpenAI,
    # set streaming to True
    # First we need to find the LLM
    llm = None
    if hasattr(langchain_object, "llm"):
        llm = langchain_object.llm
    elif hasattr(langchain_object, "llm_chain") and hasattr(langchain_object.llm_chain, "llm"):
        llm = langchain_object.llm_chain.llm

    if isinstance(llm, BaseLanguageModel):
        if hasattr(llm, "streaming") and isinstance(llm.streaming, bool):
            llm.streaming = ChatConfig.streaming
        elif hasattr(llm, "stream") and isinstance(llm.stream, bool):
            llm.stream = ChatConfig.streaming

    return langchain_object


def extract_input_variables_from_prompt(prompt: str) -> list[str]:
    variables = []
    remaining_text = prompt

    # Pattern to match single {var} and double {{var}} braces.
    pattern = r"\{\{(.*?)\}\}|\{([^{}]+)\}"

    while True:
        match = re.search(pattern, remaining_text)
        if not match:
            break

        # Extract the variable name from either the single or double brace match
        if match.group(1):  # Match found in double braces
            variable_name = "{{" + match.group(1) + "}}"  # Re-add single braces for JSON strings
        else:  # Match found in single braces
            variable_name = match.group(2)
        if variable_name is not None:
            # This means there is a match
            # but there is nothing inside the braces
            variables.append(variable_name)

        # Remove the matched text from the remaining_text
        start, end = match.span()
        remaining_text = remaining_text[:start] + remaining_text[end:]

        # Proceed to the next match until no more matches are found
        # No need to compare remaining "{}" instances because we are re-adding braces for JSON compatibility

    return variables


def setup_llm_caching():
    """Setup LLM caching."""
    settings_service = get_settings_service()
    try:
        set_langchain_cache(settings_service.settings)
    except ImportError:
        logger.warning(f"Could not import {settings_service.settings.CACHE_TYPE}. ")
    except Exception as exc:
        logger.warning(f"Could not setup LLM caching. Error: {exc}")


def set_langchain_cache(settings):
    from langchain.globals import set_llm_cache
    from dfapp.interface.importing.utils import import_class

    if cache_type := os.getenv("DFAPP_LANGCHAIN_CACHE"):
        try:
            cache_class = import_class(f"langchain_community.cache.{cache_type or settings.LANGCHAIN_CACHE}")

            logger.debug(f"Setting up LLM caching with {cache_class.__name__}")
            set_llm_cache(cache_class())
            logger.info(f"LLM caching setup with {cache_class.__name__}")
        except ImportError:
            logger.warning(f"Could not import {cache_type}. ")
    else:
        logger.info("No LLM cache set.")


def build_template_from_class(name: str, type_to_cls_dict: Dict, add_function: bool = False):
    classes = [item.__name__ for item in type_to_cls_dict.values()]

    # Raise error if name is not in chains
    if name not in classes:
        raise ValueError(f"{name} not found.")

    for _type, v in type_to_cls_dict.items():
        if v.__name__ == name:
            _class = v

            # Get the docstring
            docs = parse(_class.__doc__)

            variables = {"_type": _type}

            if "__fields__" in _class.__dict__:
                for class_field_items, value in _class.__fields__.items():
                    if class_field_items in ["callback_manager"]:
                        continue
                    variables[class_field_items] = {}
                    for name_, value_ in value.__repr_args__():
                        if name_ == "default_factory":
                            try:
                                variables[class_field_items]["default"] = get_default_factory(
                                    module=_class.__base__.__module__,
                                    function=value_,
                                )
                            except Exception:
                                variables[class_field_items]["default"] = None
                        elif name_ not in ["name"]:
                            variables[class_field_items][name_] = value_

                    variables[class_field_items]["placeholder"] = (
                        docs.params[class_field_items] if class_field_items in docs.params else ""
                    )
            base_classes = get_base_classes(_class)
            # Adding function to base classes to allow
            # the output to be a function
            if add_function:
                base_classes.append("Callable")
            return {
                "template": format_dict(variables, name),
                "description": docs.short_description or "",
                "base_classes": base_classes,
            }
