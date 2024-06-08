from typing import List, Union

from langchain.agents.agent_toolkits.vectorstore.toolkit import VectorStoreInfo, VectorStoreRouterToolkit

from dfapp.field_typing import BaseLanguageModel, Tool
from dfapp.interface.custom.custom_component import CustomComponent


class VectorStoreRouterToolkitComponent(CustomComponent):
    display_name = "VectorStoreRouterToolkit"
    description = "Toolkit for routing between Vector Stores."

    def build_config(self):
        return {
            "vectorstores": {"display_name": "Vector Stores"},
            "llm": {"display_name": "LLM"},
        }

    def build(
        self, vectorstores: List[VectorStoreInfo], llm: BaseLanguageModel
    ) -> Union[Tool, VectorStoreRouterToolkit]:
        print("vectorstores", vectorstores)
        print("llm", llm)
        return VectorStoreRouterToolkit(vectorstores=vectorstores, llm=llm)
