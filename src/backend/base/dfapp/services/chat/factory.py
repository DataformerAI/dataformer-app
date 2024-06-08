from dfapp.services.chat.service import ChatService
from dfapp.services.factory import ServiceFactory


class ChatServiceFactory(ServiceFactory):
    def __init__(self):
        super().__init__(ChatService)

    def create(self):
        # Here you would have logic to create and configure a ChatService
        return ChatService()
