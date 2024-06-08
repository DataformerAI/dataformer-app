from typing import List, Text, Union

from langchain.schema import BaseRetriever
from langchain_community.vectorstores import VectorStore
from langchain_community.vectorstores.faiss import FAISS

from dfapp.field_typing import Embeddings
from dfapp.interface.custom.custom_component import CustomComponent
from dfapp.schema.schema import Record


class FAISSComponent(CustomComponent):
    display_name = "FAISS"
    description = "Ingest documents into FAISS Vector Store."
    documentation = "https://python.langchain.com/docs/modules/data_connection/vectorstores/integrations/faiss"

    def build_config(self):
        return {
            "inputs": {"display_name": "Input", "input_types": ["Document", "Record"]},
            "embedding": {"display_name": "Embedding"},
            "folder_path": {
                "display_name": "Folder Path",
                "info": "Path to save the FAISS index. It will be relative to where Dataformer App is running.",
            },
            "index_name": {"display_name": "Index Name"},
        }

    def build(
        self,
        embedding: Embeddings,
        inputs: List[Record],
        folder_path: str,
        index_name: str = "dfapp_index",
    ) -> Union[VectorStore, FAISS, BaseRetriever]:
        documents = []
        for _input in inputs or []:
            if isinstance(_input, Record):
                documents.append(_input.to_lc_document())
            else:
                documents.append(_input)
        vector_store = FAISS.from_documents(documents=documents, embedding=embedding)
        if not folder_path:
            raise ValueError("Folder path is required to save the FAISS index.")
        path = self.resolve_path(folder_path)
        vector_store.save_local(Text(path), index_name)
        return vector_store
