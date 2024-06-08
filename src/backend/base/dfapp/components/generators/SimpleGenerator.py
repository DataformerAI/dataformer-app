from dfapp.base.models.model import LCModelComponent
from dfapp.field_typing import BaseLanguageModel


class SimpleGeneratorComponent(LCModelComponent):
    display_name = "Simple Generator"
    description = "Generate responses using a model and output text data."

    def build_config(self):
        return {
                "text": {"display name": "User Text", "required": True},
                "model": {"display_name": "Model", "info": "Input BaseLanguageModel.", "required": True},
                "system_prompt": {"display_name": "system_prompt"},
        }

    def build(self, text: str, model: BaseLanguageModel, system_prompt: str = None) -> str:
        return self.get_chat_result(model, False, text, system_prompt)
