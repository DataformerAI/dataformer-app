from dfapp.custom import CustomComponent
from dfapp.memory import get_messages, store_message
from dfapp.schema.message import Message


class StoreMessageComponent(CustomComponent):
    display_name = "Store Message"
    description = "Stores a chat message."

    def build_config(self):
        return {
            "message": {"display_name": "Message"},
        }

    def build(
        self,
        message: Message,
    ) -> Message:
        store_message(message, flow_id=self.graph.flow_id)
        self.status = get_messages()

        return message
