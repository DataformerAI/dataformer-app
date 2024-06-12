from typing import Optional

from dfapp.custom import CustomComponent
from dfapp.schema import Record


class BaseMemoryComponent(CustomComponent):
    display_name = "Chat Memory"
    description = "Retrieves stored chat messages given a specific Session ID."
    beta: bool = True
    icon = "history"

    def build_config(self):
        return {
            "sender": {
                "options": ["Machine", "User", "Machine and User"],
                "display_name": "Sender Type",
            },
            "sender_name": {"display_name": "Sender Name", "advanced": True},
            "n_messages": {
                "display_name": "Number of Messages",
                "info": "Number of messages to retrieve.",
            },
            "session_id": {
                "display_name": "Session ID",
                "info": "Session ID of the chat history.",
                "input_types": ["Text"],
            },
            "order": {
                "options": ["Ascending", "Descending"],
                "display_name": "Order",
                "info": "Order of the messages.",
                "advanced": True,
            },
            "record_template": {
                "display_name": "Record Template",
                "multiline": True,
                "info": "Template to convert Record to Text. If left empty, it will be dynamically set to the Record's text key.",
                "advanced": True,
            },
        }

    def get_messages(self, **kwargs) -> list[Record]:
        raise NotImplementedError

    def add_message(
        self, sender: str, sender_name: str, text: str, session_id: str, metadata: Optional[dict] = None, **kwargs
    ):
        raise NotImplementedError
