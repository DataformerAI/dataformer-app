from langchain import tools
from langchain.agents import Tool
from langchain.agents.load_tools import _BASE_TOOLS, _EXTRA_LLM_TOOLS, _EXTRA_OPTIONAL_TOOLS, _LLM_TOOLS
from langchain_community.tools.json.tool import JsonSpec

from dfapp.interface.importing.utils import import_class
from dfapp.interface.tools.custom import PythonFunctionTool

FILE_TOOLS = {"JsonSpec": JsonSpec}
CUSTOM_TOOLS = {
    "Tool": Tool,
    "PythonFunctionTool": PythonFunctionTool,
}

OTHER_TOOLS = {tool: import_class(f"langchain_community.tools.{tool}") for tool in tools.__all__}

ALL_TOOLS_NAMES = {
    **_BASE_TOOLS,
    **_LLM_TOOLS,  # type: ignore
    **{k: v[0] for k, v in _EXTRA_LLM_TOOLS.items()},  # type: ignore
    **{k: v[0] for k, v in _EXTRA_OPTIONAL_TOOLS.items()},
    **CUSTOM_TOOLS,
    **FILE_TOOLS,  # type: ignore
    **OTHER_TOOLS,
}
