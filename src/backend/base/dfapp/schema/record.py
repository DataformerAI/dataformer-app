import copy
import json
from typing import Optional, cast

from langchain_core.documents import Document
from langchain_core.messages import AIMessage, BaseMessage, HumanMessage, SystemMessage
from langchain_core.prompt_values import ImagePromptValue
from langchain_core.prompts.image import ImagePromptTemplate
from pydantic import BaseModel, model_serializer, model_validator


class Record(BaseModel):
    """
    Represents a record with text and optional data.

    Attributes:
        data (dict, optional): Additional data associated with the record.
    """

    text_key: str = "text"
    data: dict = {}
    default_value: Optional[str] = ""

    @model_validator(mode="before")
    def validate_data(cls, values):
        if not values.get("data"):
            values["data"] = {}
        # Any other keyword should be added to the data dictionary
        for key in values:
            if key not in values["data"] and key not in {"text_key", "data", "default_value"}:
                values["data"][key] = values[key]
        return values

    @model_serializer(mode="plain", when_used="json")
    def serialize_model(self):
        data = {k: v.to_json() if hasattr(v, "to_json") else v for k, v in self.data.items()}
        return data

    def get_text(self):
        """
        Retrieves the text value from the data dictionary.

        If the text key is present in the data dictionary, the corresponding value is returned.
        Otherwise, the default value is returned.

        Returns:
            The text value from the data dictionary or the default value.
        """
        return self.data.get(self.text_key, self.default_value)

    @classmethod
    def from_document(cls, document: Document) -> "Record":
        """
        Converts a Document to a Record.

        Args:
            document (Document): The Document to convert.

        Returns:
            Record: The converted Record.
        """
        data = document.metadata
        data["text"] = document.page_content
        return cls(data=data, text_key="text")

    @classmethod
    def from_lc_message(cls, message: BaseMessage) -> "Record":
        """
        Converts a BaseMessage to a Record.

        Args:
            message (BaseMessage): The BaseMessage to convert.

        Returns:
            Record: The converted Record.
        """
        data: dict = {"text": message.content}
        data["metadata"] = cast(dict, message.to_json())
        return cls(data=data, text_key="text")

    def __add__(self, other: "Record") -> "Record":
        """
        Combines the data of two records by attempting to add values for overlapping keys
        for all types that support the addition operation. Falls back to the value from 'other'
        record when addition is not supported.
        """
        combined_data = self.data.copy()
        for key, value in other.data.items():
            # If the key exists in both records and both values support the addition operation
            if key in combined_data:
                try:
                    combined_data[key] += value
                except TypeError:
                    # Fallback: Use the value from 'other' record if addition is not supported
                    combined_data[key] = value
            else:
                # If the key is not in the first record, simply add it
                combined_data[key] = value

        return Record(data=combined_data)

    def to_lc_document(self) -> Document:
        """
        Converts the Record to a Document.

        Returns:
            Document: The converted Document.
        """
        text = self.data.pop(self.text_key, self.default_value)
        return Document(page_content=text, metadata=self.data)

    def to_lc_message(
        self,
    ) -> HumanMessage | SystemMessage:
        """
        Converts the Record to a BaseMessage.

        Returns:
            BaseMessage: The converted BaseMessage.
        """
        # The idea of this function is to be a helper to convert a Record to a BaseMessage
        # It will use the "sender" key to determine if the message is Human or AI
        # If the key is not present, it will default to AI
        # But first we check if all required keys are present in the data dictionary
        # they are: "text", "sender"
        if not all(key in self.data for key in ["text", "sender"]):
            raise ValueError(f"Missing required keys ('text', 'sender') in Record: {self.data}")
        sender = self.data.get("sender", "Machine")
        text = self.data.get("text", "")
        files = self.data.get("files", [])
        if sender == "User":
            if files:
                contents = [{"type": "text", "text": text}]
                for file_path in files:
                    image_template = ImagePromptTemplate()
                    image_prompt_value: ImagePromptValue = image_template.invoke(input={"path": file_path})
                    contents.append({"type": "image_url", "image_url": image_prompt_value.image_url})
                human_message = HumanMessage(content=contents)
            else:
                human_message = HumanMessage(
                    content=[{"type": "text", "text": text}],
                )

            return human_message

        return AIMessage(content=text)

    def __getattr__(self, key):
        """
        Allows attribute-like access to the data dictionary.
        """
        try:
            if key.startswith("__"):
                return self.__getattribute__(key)
            if key in {"data", "text_key"} or key.startswith("_"):
                return super().__getattr__(key)

            return self.data.get(key, self.default_value)
        except KeyError:
            # Fallback to default behavior to raise AttributeError for undefined attributes
            raise AttributeError(f"'{type(self).__name__}' object has no attribute '{key}'")

    def __setattr__(self, key, value):
        """
        Allows attribute-like setting of values in the data dictionary,
        while still allowing direct assignment to class attributes.
        """
        if key in {"data", "text_key"} or key.startswith("_"):
            super().__setattr__(key, value)
        else:
            self.data[key] = value

    def __delattr__(self, key):
        """
        Allows attribute-like deletion from the data dictionary.
        """
        if key in {"data", "text_key"} or key.startswith("_"):
            super().__delattr__(key)
        else:
            del self.data[key]

    def __deepcopy__(self, memo):
        """
        Custom deepcopy implementation to handle copying of the Record object.
        """
        # Create a new Record object with a deep copy of the data dictionary
        return Record(data=copy.deepcopy(self.data, memo), text_key=self.text_key, default_value=self.default_value)

    # check which attributes the Record has by checking the keys in the data dictionary
    def __dir__(self):
        return super().__dir__() + list(self.data.keys())

    def __str__(self) -> str:
        # return a JSON string representation of the Record atributes
        try:
            data = {k: v.to_json() if hasattr(v, "to_json") else v for k, v in self.data.items()}
            return json.dumps(data, indent=4)
        except Exception:
            return str(self.data)

    def __contains__(self, key):
        return key in self.data

    def __eq__(self, other):
        return isinstance(other, Record) and self.data == other.data
