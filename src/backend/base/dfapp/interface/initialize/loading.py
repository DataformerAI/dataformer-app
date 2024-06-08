import inspect
import json
from typing import TYPE_CHECKING, Any, Callable, Dict, Sequence, Type


import orjson
from langchain.agents import agent as agent_module
from langchain.agents.agent import AgentExecutor
from langchain.agents.agent_toolkits.base import BaseToolkit
from langchain.agents.tools import BaseTool
from langchain.chains.base import Chain
from langchain.document_loaders.base import BaseLoader
from langchain_community.vectorstores import VectorStore
from langchain_core.documents import Document
from loguru import logger
from pydantic import ValidationError

from dfapp.interface.custom.eval import eval_custom_component_code
from dfapp.interface.importing.utils import import_by_type
from dfapp.interface.initialize.llm import initialize_vertexai
from dfapp.interface.initialize.utils import handle_format_kwargs, handle_node_type, handle_partial_variables
from dfapp.interface.initialize.vector_store import vecstore_initializer
from dfapp.interface.retrievers.base import retriever_creator
from dfapp.interface.toolkits.base import toolkits_creator
from dfapp.interface.utils import load_file_into_dict
from dfapp.interface.wrappers.base import wrapper_creator
from dfapp.schema.schema import Record
from dfapp.utils import validate
from dfapp.utils.util import unescape_string

if TYPE_CHECKING:
    from dfapp.custom import CustomComponent
    from dfapp.graph.vertex.base import Vertex


async def instantiate_class(
    vertex: "Vertex",
    user_id=None,
) -> Any:
    """Instantiate class from module type and key, and params"""
    from dfapp.interface.custom_lists import CUSTOM_NODES

    vertex_type = vertex.vertex_type
    base_type = vertex.base_type
    params = vertex.params
    params = convert_params_to_sets(params)
    params = convert_kwargs(params)

    if vertex_type in CUSTOM_NODES:
        if custom_node := CUSTOM_NODES.get(vertex_type):
            if hasattr(custom_node, "initialize"):
                return custom_node.initialize(**params)
            if callable(custom_node):
                return custom_node(**params)
            raise ValueError(f"Custom node {vertex_type} is not callable")
    logger.debug(f"Instantiating {vertex_type} of type {base_type}")
    if not base_type:
        raise ValueError("No base type provided for vertex")
    if base_type == "custom_components":
        return await instantiate_custom_component(params, user_id, vertex)
    class_object = import_by_type(_type=base_type, name=vertex_type)
    return await instantiate_based_on_type(
        class_object=class_object,
        base_type=base_type,
        node_type=vertex_type,
        params=params,
        user_id=user_id,
        vertex=vertex,
    )


def convert_params_to_sets(params):
    """Convert certain params to sets"""
    if "allowed_special" in params:
        params["allowed_special"] = set(params["allowed_special"])
    if "disallowed_special" in params:
        params["disallowed_special"] = set(params["disallowed_special"])
    return params


def convert_kwargs(params):
    # if *kwargs are passed as a string, convert to dict
    # first find any key that has kwargs or config in it
    kwargs_keys = [key for key in params.keys() if "kwargs" in key or "config" in key]
    for key in kwargs_keys:
        if isinstance(params[key], str):
            try:
                params[key] = orjson.loads(params[key])
            except json.JSONDecodeError:
                # if the string is not a valid json string, we will
                # remove the key from the params
                params.pop(key, None)
    return params


async def instantiate_based_on_type(
    class_object,
    base_type,
    node_type,
    params,
    user_id,
    vertex,
):
    if base_type == "agents":
        return instantiate_agent(node_type, class_object, params)
    elif base_type == "prompts":
        return instantiate_prompt(node_type, class_object, params)
    elif base_type == "tools":
        tool = instantiate_tool(node_type, class_object, params)
        if hasattr(tool, "name") and isinstance(tool, BaseTool):
            # tool name shouldn't contain spaces
            tool.name = tool.name.replace(" ", "_")
        return tool
    elif base_type == "toolkits":
        return instantiate_toolkit(node_type, class_object, params)
    elif base_type == "embeddings":
        return instantiate_embedding(node_type, class_object, params)
    elif base_type == "vectorstores":
        return instantiate_vectorstore(class_object, params)
    elif base_type == "documentloaders":
        return instantiate_documentloader(node_type, class_object, params)
    elif base_type == "textsplitters":
        return instantiate_textsplitter(class_object, params)
    elif base_type == "utilities":
        return instantiate_utility(node_type, class_object, params)
    elif base_type == "chains":
        return instantiate_chains(node_type, class_object, params)
    elif base_type == "models":
        return instantiate_llm(node_type, class_object, params)
    elif base_type == "retrievers":
        return instantiate_retriever(node_type, class_object, params)
    elif base_type == "memory":
        return instantiate_memory(node_type, class_object, params)
    elif base_type == "custom_components":
        return await instantiate_custom_component(
            params,
            user_id,
            vertex,
        )
    elif base_type == "wrappers":
        return instantiate_wrapper(node_type, class_object, params)
    else:
        return class_object(**params)


def update_params_with_load_from_db_fields(custom_component: "CustomComponent", params, load_from_db_fields):
    # For each field in load_from_db_fields, we will check if it's in the params
    # and if it is, we will get the value from the custom_component.keys(name)
    # and update the params with the value
    for field in load_from_db_fields:
        if field in params:
            try:
                key = custom_component.variables(params[field])
                params[field] = key if key else params[field]
            except Exception as exc:
                logger.error(f"Failed to get value for {field} from custom component. Error: {exc}")
                pass
    return params


async def instantiate_custom_component(params, user_id, vertex):
    params_copy = params.copy()
    class_object: Type["CustomComponent"] = eval_custom_component_code(params_copy.pop("code"))
    custom_component: "CustomComponent" = class_object(
        user_id=user_id,
        parameters=params_copy,
        vertex=vertex,
        selected_output_type=vertex.selected_output_type,
    )
    params_copy = update_params_with_load_from_db_fields(custom_component, params_copy, vertex.load_from_db_fields)

    if "retriever" in params_copy and hasattr(params_copy["retriever"], "as_retriever"):
        params_copy["retriever"] = params_copy["retriever"].as_retriever()

    # Determine if the build method is asynchronous
    is_async = inspect.iscoroutinefunction(custom_component.build)

    if is_async:
        # Await the build method directly if it's async
        build_result = await custom_component.build(**params_copy)
    else:
        # Call the build method directly if it's sync
        build_result = custom_component.build(**params_copy)
    custom_repr = custom_component.custom_repr()
    if custom_repr is None and isinstance(build_result, (dict, Record, str)):
        custom_repr = build_result
    if not isinstance(custom_repr, str):
        custom_repr = str(custom_repr)
    return custom_component, build_result, {"repr": custom_repr}


def instantiate_wrapper(node_type, class_object, params):
    if node_type in wrapper_creator.from_method_nodes:
        method = wrapper_creator.from_method_nodes[node_type]
        if class_method := getattr(class_object, method, None):
            return class_method(**params)
        raise ValueError(f"Method {method} not found in {class_object}")
    return class_object(**params)


def instantiate_llm(node_type, class_object, params: Dict):
    # This is a workaround so JinaChat works until streaming is implemented
    # if "openai_api_base" in params and "jina" in params["openai_api_base"]:
    # False if condition is True
    if "VertexAI" in node_type:
        return initialize_vertexai(class_object=class_object, params=params)
    # max_tokens sometimes is a string and should be an int
    if "max_tokens" in params:
        if isinstance(params["max_tokens"], str) and params["max_tokens"].isdigit():
            params["max_tokens"] = int(params["max_tokens"])
        elif not isinstance(params.get("max_tokens"), int):
            params.pop("max_tokens", None)
    return class_object(**params)


def instantiate_memory(node_type, class_object, params):
    # process input_key and output_key to remove them if
    # they are empty strings
    if node_type == "ConversationEntityMemory":
        params.pop("memory_key", None)

    for key in ["input_key", "output_key"]:
        if key in params and (params[key] == "" or not params[key]):
            params.pop(key)

    try:
        if "retriever" in params and hasattr(params["retriever"], "as_retriever"):
            params["retriever"] = params["retriever"].as_retriever()
        return class_object(**params)
    # I want to catch a specific attribute error that happens
    # when the object does not have a cursor attribute
    except Exception as exc:
        if "object has no attribute 'cursor'" in str(exc) or 'object has no field "conn"' in str(exc):
            raise AttributeError(
                (
                    "Failed to build connection to database."
                    f" Please check your connection string and try again. Error: {exc}"
                )
            ) from exc
        raise exc


def instantiate_retriever(node_type, class_object, params):
    if "retriever" in params and hasattr(params["retriever"], "as_retriever"):
        params["retriever"] = params["retriever"].as_retriever()
    if node_type in retriever_creator.from_method_nodes:
        method = retriever_creator.from_method_nodes[node_type]
        if class_method := getattr(class_object, method, None):
            return class_method(**params)
        raise ValueError(f"Method {method} not found in {class_object}")
    return class_object(**params)


def instantiate_chains(node_type, class_object: Type[Chain], params: Dict):
    from dfapp.interface.chains.base import chain_creator

    if "retriever" in params and hasattr(params["retriever"], "as_retriever"):
        params["retriever"] = params["retriever"].as_retriever()
    if node_type in chain_creator.from_method_nodes:
        method = chain_creator.from_method_nodes[node_type]
        if class_method := getattr(class_object, method, None):
            return class_method(**params)
        raise ValueError(f"Method {method} not found in {class_object}")

    return class_object(**params)


def instantiate_agent(node_type, class_object: Type[agent_module.Agent], params: Dict):
    from dfapp.interface.agents.base import agent_creator

    if node_type in agent_creator.from_method_nodes:
        method = agent_creator.from_method_nodes[node_type]
        if class_method := getattr(class_object, method, None):
            agent = class_method(**params)
            tools = params.get("tools", [])
            return AgentExecutor.from_agent_and_tools(agent=agent, tools=tools, handle_parsing_errors=True)
    return load_agent_executor(class_object, params)


def instantiate_prompt(node_type, class_object, params: Dict):
    params, prompt = handle_node_type(node_type, class_object, params)
    format_kwargs = handle_format_kwargs(prompt, params)
    # Now we'll use partial_format to format the prompt
    if format_kwargs:
        prompt = handle_partial_variables(prompt, format_kwargs)
    return prompt, format_kwargs


def instantiate_tool(node_type, class_object: Type[BaseTool], params: Dict):
    if node_type == "JsonSpec":
        if file_dict := load_file_into_dict(params.pop("path")):
            params["dict_"] = file_dict
        else:
            raise ValueError("Invalid file")
        return class_object(**params)
    elif node_type == "PythonFunctionTool":
        from dfapp.interface.custom.utils import get_function

        params["func"] = get_function(params.get("code"))
        return class_object(**params)
    elif node_type == "PythonFunction":
        function_string = params["code"]
        if isinstance(function_string, str):
            return validate.eval_function(function_string)
        raise ValueError("Function should be a string")
    elif node_type.lower() == "tool":
        return class_object(**params)
    return class_object(**params)


def instantiate_toolkit(node_type, class_object: Type[BaseToolkit], params: Dict):
    loaded_toolkit = class_object(**params)
    # Commenting this out for now to use toolkits as normal tools
    # if toolkits_creator.has_create_function(node_type):
    #     return load_toolkits_executor(node_type, loaded_toolkit, params)
    if isinstance(loaded_toolkit, BaseToolkit):
        return loaded_toolkit.get_tools()
    return loaded_toolkit


def instantiate_embedding(node_type, class_object, params: Dict):
    params.pop("model", None)
    params.pop("headers", None)

    if "VertexAI" in node_type:
        return initialize_vertexai(class_object=class_object, params=params)

    if "OpenAIEmbedding" in node_type:
        params["disallowed_special"] = ()

    try:
        return class_object(**params)
    except ValidationError:
        params = {key: value for key, value in params.items() if key in class_object.model_fields}
        return class_object(**params)


def instantiate_vectorstore(class_object: Type[VectorStore], params: Dict):
    search_kwargs = params.pop("search_kwargs", {})
    if search_kwargs == {"yourkey": "value"}:
        search_kwargs = {}
    # clean up docs or texts to have only documents
    if "texts" in params:
        params["documents"] = params.pop("texts")
    if "documents" in params:
        params["documents"] = [doc for doc in params["documents"] if isinstance(doc, Document)]
    if initializer := vecstore_initializer.get(class_object.__name__):
        vecstore = initializer(class_object, params)
    else:
        if "texts" in params:
            params["documents"] = params.pop("texts")
        vecstore = class_object.from_documents(**params)

    # ! This might not work. Need to test
    if search_kwargs and hasattr(vecstore, "as_retriever"):
        vecstore = vecstore.as_retriever(search_kwargs=search_kwargs)

    return vecstore


def instantiate_documentloader(node_type: str, class_object: Type[BaseLoader], params: Dict):
    if "file_filter" in params:
        # file_filter will be a string but we need a function
        # that will be used to filter the files using file_filter
        # like lambda x: x.endswith(".txt") but as we don't know
        # anything besides the string, we will simply check if the string is
        # in x and if it is, we will return True
        file_filter = params.pop("file_filter")
        extensions = file_filter.split(",")
        params["file_filter"] = lambda x: any(extension.strip() in x for extension in extensions)
    metadata = params.pop("metadata", None)
    if metadata and isinstance(metadata, str):
        try:
            metadata = orjson.loads(metadata)
        except json.JSONDecodeError as exc:
            raise ValueError("The metadata you provided is not a valid JSON string.") from exc

    if node_type == "WebBaseLoader":
        if web_path := params.pop("web_path", None):
            params["web_paths"] = [web_path]

    docs = class_object(**params).load()
    # Now if metadata is an empty dict, we will not add it to the documents
    if metadata:
        for doc in docs:
            # If the document already has metadata, we will not overwrite it
            if not doc.metadata:
                doc.metadata = metadata
            else:
                doc.metadata.update(metadata)

    return docs


def instantiate_textsplitter(
    class_object,
    params: Dict,
):
    try:
        documents = params.pop("documents")
        if not isinstance(documents, list):
            documents = [documents]
    except KeyError as exc:
        raise ValueError(
            "The source you provided did not load correctly or was empty."
            "Try changing the chunk_size of the Text Splitter."
        ) from exc

    if ("separator_type" in params and params["separator_type"] == "Text") or "separator_type" not in params:
        params.pop("separator_type", None)
        # separators might come in as an escaped string like \\n
        # so we need to convert it to a string
        if "separators" in params:
            if isinstance(params["separators"], str):
                params["separators"] = unescape_string(params["separators"])
            elif isinstance(params["separators"], list):
                params["separators"] = [unescape_string(separator) for separator in params["separators"]]
        text_splitter = class_object(**params)
    else:
        from langchain.text_splitter import Language

        language = params.pop("separator_type", None)
        params["language"] = Language(language)
        params.pop("separators", None)

        text_splitter = class_object.from_language(**params)
    return text_splitter.split_documents(documents)


def instantiate_utility(node_type, class_object, params: Dict):
    if node_type == "SQLDatabase":
        return class_object.from_uri(params.pop("uri"))
    return class_object(**params)


def replace_zero_shot_prompt_with_prompt_template(nodes):
    """Replace ZeroShotPrompt with PromptTemplate"""
    for node in nodes:
        if node["data"]["type"] == "ZeroShotPrompt":
            # Build Prompt Template
            tools = [
                tool
                for tool in nodes
                if tool["type"] != "chatOutputNode" and "Tool" in tool["data"]["node"]["base_classes"]
            ]
            node["data"] = build_prompt_template(prompt=node["data"], tools=tools)
            break
    return nodes


def load_agent_executor(agent_class: type[agent_module.Agent], params, **kwargs):
    """Load agent executor from agent class, tools and chain"""
    allowed_tools: Sequence[BaseTool] = params.get("allowed_tools", [])
    llm_chain = params["llm_chain"]
    # agent has hidden args for memory. might need to be support
    # memory = params["memory"]
    # if allowed_tools is not a list or set, make it a list
    if not isinstance(allowed_tools, (list, set)) and isinstance(allowed_tools, BaseTool):
        allowed_tools = [allowed_tools]
    tool_names = [tool.name for tool in allowed_tools]
    # Agent class requires an output_parser but Agent classes
    # have a default output_parser.
    agent = agent_class(allowed_tools=tool_names, llm_chain=llm_chain)  # type: ignore
    return AgentExecutor.from_agent_and_tools(
        agent=agent,
        tools=allowed_tools,
        handle_parsing_errors=True,
        # memory=memory,
        **kwargs,
    )


def load_toolkits_executor(node_type: str, toolkit: BaseToolkit, params: dict):
    create_function: Callable = toolkits_creator.get_create_function(node_type)
    if llm := params.get("llm"):
        return create_function(llm=llm, toolkit=toolkit)


def build_prompt_template(prompt, tools):
    """Build PromptTemplate from ZeroShotPrompt"""
    prefix = prompt["node"]["template"]["prefix"]["value"]
    suffix = prompt["node"]["template"]["suffix"]["value"]
    format_instructions = prompt["node"]["template"]["format_instructions"]["value"]

    tool_strings = "\n".join(
        [f"{tool['data']['node']['name']}: {tool['data']['node']['description']}" for tool in tools]
    )
    tool_names = ", ".join([tool["data"]["node"]["name"] for tool in tools])
    format_instructions = format_instructions.format(tool_names=tool_names)
    value = "\n\n".join([prefix, tool_strings, format_instructions, suffix])

    prompt["type"] = "PromptTemplate"

    prompt["node"] = {
        "template": {
            "_type": "prompt",
            "input_variables": {
                "type": "str",
                "required": True,
                "placeholder": "",
                "list": True,
                "show": False,
                "multiline": False,
            },
            "template": {
                "type": "str",
                "required": True,
                "placeholder": "",
                "list": False,
                "show": True,
                "multiline": True,
                "value": value,
            },
            "template_format": {
                "type": "str",
                "required": False,
                "placeholder": "",
                "list": False,
                "show": False,
                "multline": False,
                "value": "f-string",
            },
            "validate_template": {
                "type": "bool",
                "required": False,
                "placeholder": "",
                "list": False,
                "show": False,
                "multline": False,
                "value": True,
            },
        },
        "description": "Schema to represent a prompt for an LLM.",
        "base_classes": ["BasePromptTemplate"],
    }

    return prompt
