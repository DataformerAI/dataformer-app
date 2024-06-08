from langchain.agents import AgentExecutor, create_json_agent
from langchain_community.agent_toolkits.json.toolkit import JsonToolkit

from dfapp.field_typing import (
    BaseLanguageModel,
)
from dfapp.interface.custom.custom_component import CustomComponent


class JsonAgentComponent(CustomComponent):
    display_name = "JsonAgent"
    description = "Construct a json agent from an LLM and tools."

    def build_config(self):
        return {
            "llm": {"display_name": "LLM"},
            "toolkit": {"display_name": "Toolkit"},
        }

    def build(
        self,
        llm: BaseLanguageModel,
        toolkit: JsonToolkit,
    ) -> AgentExecutor:
        return create_json_agent(llm=llm, toolkit=toolkit)
