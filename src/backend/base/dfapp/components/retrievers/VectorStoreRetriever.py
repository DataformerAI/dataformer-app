from langchain_core.vectorstores import VectorStoreRetriever

from dfapp.field_typing import VectorStore
from dfapp.interface.custom.custom_component import CustomComponent


class VectoStoreRetrieverComponent(CustomComponent):
    display_name = "VectorStore Retriever"
    description = "A vector store retriever"

    def build_config(self):
        return {
            "vectorstore": {"display_name": "Vector Store", "type": VectorStore},
        }

    def build(self, vectorstore: VectorStore) -> VectorStoreRetriever:
        return vectorstore.as_retriever()
