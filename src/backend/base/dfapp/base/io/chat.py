from typing import Optional, Union

from dfapp.base.data.utils import IMG_FILE_TYPES, TEXT_FILE_TYPES
from dfapp.custom import CustomComponent
from dfapp.memory import store_message
from dfapp.schema import Record
from dfapp.schema.message import Message


class ChatComponent(CustomComponent):
    display_name = "Chat Component"
    description = "Use as base for chat components."

    def build_config(self):
        return {
            "input_value": {
                "input_types": ["Text"],
                "display_name": "Text",
                "multiline": True,
            },
            "sender": {
                "options": ["Machine", "User"],
                "display_name": "Sender Type",
                "advanced": True,
            },
            "sender_name": {"display_name": "Sender Name", "advanced": True},
            "session_id": {
                "display_name": "Session ID",
                "info": "If provided, the message will be stored in the memory.",
                "advanced": True,
            },
            "return_message": {
                "display_name": "Return Message",
                "info": "Return the message as a Message containing the sender, sender_name, and session_id.",
                "advanced": True,
            },
            "record_template": {
                "display_name": "Record Template",
                "multiline": True,
                "info": "In case of Message being a Record, this template will be used to convert it to text.",
                "advanced": True,
            },
            "files": {
                "field_type": "file",
                "display_name": "Files",
                "file_types": TEXT_FILE_TYPES + IMG_FILE_TYPES,
                "info": "Files to be sent with the message.",
                "advanced": True,
            },
        }

    def store_message(
        self,
        message: Message,
    ) -> list[Message]:
        messages = store_message(
            message,
            flow_id=self.graph.flow_id,
        )

        self.status = messages
        return messages

    def build_with_record(
        self,
        sender: Optional[str] = "User",
        sender_name: Optional[str] = "User",
        input_value: Optional[Union[str, Record, Message]] = None,
        files: Optional[list[str]] = None,
        session_id: Optional[str] = None,
        return_message: Optional[bool] = False,
    ) -> Message:
        message: Message | None = None

        if isinstance(input_value, Record):
            # Update the data of the record
            message = Message.from_record(input_value)
        else:
            message = Message(
                text=input_value, sender=sender, sender_name=sender_name, files=files, session_id=session_id
            )
        if not return_message:
            message_text = message.text
        else:
            message_text = message

        self.status = message_text
        if session_id and isinstance(message, Message) and isinstance(message.text, str):
            self.store_message(message)
        return message_text
