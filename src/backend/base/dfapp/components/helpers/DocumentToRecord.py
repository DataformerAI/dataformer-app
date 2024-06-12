from typing import List

from langchain_core.documents import Document

from dfapp.custom import CustomComponent
from dfapp.schema import Record


class DocumentToRecordComponent(CustomComponent):
    display_name = "Documents To Records"
    description = "Convert LangChain Documents into Records."

    field_config = {
        "documents": {"display_name": "Documents"},
    }

    def build(self, documents: List[Document]) -> List[Record]:
        if isinstance(documents, Document):
            documents = [documents]
        records = [Record.from_document(document) for document in documents]
        self.status = records
        return records
