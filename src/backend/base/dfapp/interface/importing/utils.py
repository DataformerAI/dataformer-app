# This module is used to import any langchain class by name.

import importlib
from typing import Any, Type

from langchain.agents import Agent
from langchain.base_language import BaseLanguageModel
from langchain.chains.base import Chain
from langchain.prompts import PromptTemplate
from langchain.tools import BaseTool
from langchain_core.language_models.chat_models import BaseChatModel

from dfapp.interface.wrappers.base import wrapper_creator


def import_module(module_path: str) -> Any:
    """Import module from module path"""
    if "from" not in module_path:
        # Import the module using the module path
        return importlib.import_module(module_path)
    # Split the module path into its components
    _, module_path, _, object_name = module_path.split()

    # Import the module using the module path
    module = importlib.import_module(module_path)

    return getattr(module, object_name)


def import_by_type(_type: str, name: str) -> Any:
    """Import class by type and name"""
    if _type is None:
        raise ValueError(f"Type cannot be None. Check if {name} is in the config file.")
    func_dict = {
        "agents": import_agent,
        "prompts": import_prompt,
        "models": {"llm": import_llm, "chat": import_chat_llm},
        "tools": import_tool,
        "chains": import_chain,
        "toolkits": import_toolkit,
        "wrappers": import_wrapper,
        "memory": import_memory,
        "embeddings": import_embedding,
        "vectorstores": import_vectorstore,
        "documentloaders": import_documentloader,
        "textsplitters": import_textsplitter,
        "utilities": import_utility,
        "retrievers": import_retriever,
    }
    if _type == "models":
        key = "chat" if "chat" in name.lower() else "llm"
        loaded_func = func_dict[_type][key]  # type: ignore
    else:
        loaded_func = func_dict[_type]

    return loaded_func(name)


def import_chat_llm(llm: str) -> BaseChatModel:
    """Import chat llm from llm name"""
    return import_class(f"langchain_community.chat_models.{llm}")


def import_retriever(retriever: str) -> Any:
    """Import retriever from retriever name"""
    return import_module(f"from langchain.retrievers import {retriever}")


def import_memory(memory: str) -> Any:
    """Import memory from memory name"""
    return import_module(f"from langchain.memory import {memory}")


def import_class(class_path: str) -> Any:
    """Import class from class path"""
    module_path, class_name = class_path.rsplit(".", 1)
    module = import_module(module_path)
    return getattr(module, class_name)


def import_prompt(prompt: str) -> Type[PromptTemplate]:
    """Import prompt from prompt name"""
    from dfapp.interface.prompts.custom import CUSTOM_PROMPTS

    if prompt == "ZeroShotPrompt":
        return import_class("langchain.prompts.PromptTemplate")
    elif prompt in CUSTOM_PROMPTS:
        return CUSTOM_PROMPTS[prompt]
    return import_class(f"langchain.prompts.{prompt}")


def import_wrapper(wrapper: str) -> Any:
    """Import wrapper from wrapper name"""
    if isinstance(wrapper_creator.type_dict, dict) and wrapper in wrapper_creator.type_dict:
        return wrapper_creator.type_dict.get(wrapper)


def import_toolkit(toolkit: str) -> Any:
    """Import toolkit from toolkit name"""
    return import_module(f"from langchain.agents.agent_toolkits import {toolkit}")


def import_agent(agent: str) -> Agent:
    """Import agent from agent name"""
    # check for custom agent

    return import_class(f"langchain.agents.{agent}")


def import_llm(llm: str) -> BaseLanguageModel:
    """Import llm from llm name"""
    return import_class(f"langchain.llms.{llm}")


def import_tool(tool: str) -> BaseTool:
    """Import tool from tool name"""
    from dfapp.interface.tools.base import tool_creator

    if tool in tool_creator.type_to_loader_dict:
        return tool_creator.type_to_loader_dict[tool]["fcn"]

    return import_class(f"langchain.tools.{tool}")


def import_chain(chain: str) -> Type[Chain]:
    """Import chain from chain name"""
    from dfapp.interface.chains.custom import CUSTOM_CHAINS

    if chain in CUSTOM_CHAINS:
        return CUSTOM_CHAINS[chain]
    if chain == "SQLDatabaseChain":
        return import_class("langchain_experimental.sql.SQLDatabaseChain")
    return import_class(f"langchain.chains.{chain}")


def import_embedding(embedding: str) -> Any:
    """Import embedding from embedding name"""
    return import_class(f"langchain_community.embeddings.{embedding}")


def import_vectorstore(vectorstore: str) -> Any:
    """Import vectorstore from vectorstore name"""
    return import_class(f"langchain_community.vectorstores.{vectorstore}")


def import_documentloader(documentloader: str) -> Any:
    """Import documentloader from documentloader name"""
    return import_class(f"langchain_community.document_loaders.{documentloader}")


def import_textsplitter(textsplitter: str) -> Any:
    """Import textsplitter from textsplitter name"""
    return import_class(f"langchain.text_splitter.{textsplitter}")


def import_utility(utility: str) -> Any:
    """Import utility from utility name"""
    if utility == "SQLDatabase":
        return import_class(f"langchain_community.sql_database.{utility}")
    return import_class(f"langchain_community.utilities.{utility}")
