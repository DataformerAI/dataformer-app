from dfapp.graph.vertex import types
from dfapp.interface.agents.base import agent_creator
from dfapp.interface.custom.base import custom_component_creator
from dfapp.interface.document_loaders.base import documentloader_creator
from dfapp.interface.embeddings.base import embedding_creator
from dfapp.interface.llms.base import llm_creator
from dfapp.interface.memories.base import memory_creator
from dfapp.interface.prompts.base import prompt_creator
from dfapp.interface.retrievers.base import retriever_creator
from dfapp.interface.text_splitters.base import textsplitter_creator
from dfapp.interface.toolkits.base import toolkits_creator
from dfapp.interface.tools.base import tool_creator
from dfapp.interface.wrappers.base import wrapper_creator
from dfapp.utils.lazy_load import LazyLoadDictBase

CHAT_COMPONENTS = ["ChatInput", "ChatOutput", "TextInput", "SessionID"]


class VertexTypesDict(LazyLoadDictBase):
    def __init__(self):
        self._all_types_dict = None

    @property
    def VERTEX_TYPE_MAP(self):
        return self.all_types_dict

    def _build_dict(self):
        langchain_types_dict = self.get_type_dict()
        return {
            **langchain_types_dict,
            "Custom": ["Custom Tool", "Python Function"],
        }

    def get_type_dict(self):
        return {
            **{t: types.PromptVertex for t in prompt_creator.to_list()},
            **{t: types.AgentVertex for t in agent_creator.to_list()},
            # **{t: types.ChainVertex for t in chain_creator.to_list()},
            **{t: types.ToolVertex for t in tool_creator.to_list()},
            **{t: types.ToolkitVertex for t in toolkits_creator.to_list()},
            **{t: types.WrapperVertex for t in wrapper_creator.to_list()},
            **{t: types.LLMVertex for t in llm_creator.to_list()},
            **{t: types.MemoryVertex for t in memory_creator.to_list()},
            **{t: types.EmbeddingVertex for t in embedding_creator.to_list()},
            # **{t: types.VectorStoreVertex for t in vectorstore_creator.to_list()},
            **{t: types.DocumentLoaderVertex for t in documentloader_creator.to_list()},
            **{t: types.TextSplitterVertex for t in textsplitter_creator.to_list()},
            **{t: types.CustomComponentVertex for t in custom_component_creator.to_list()},
            **{t: types.RetrieverVertex for t in retriever_creator.to_list()},
            **{t: types.ChatVertex for t in CHAT_COMPONENTS},
        }

    def get_custom_component_vertex_type(self):
        return types.CustomComponentVertex


lazy_load_vertex_dict = VertexTypesDict()
