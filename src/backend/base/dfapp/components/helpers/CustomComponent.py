# from dfapp.field_typing import Data
from dfapp.custom import CustomComponent
from dfapp.schema import Record


class Component(CustomComponent):
    display_name = "Custom Component"
    description = "Use as a template to create your own component."
    documentation: str = "http://docs.dataformer.ai/components/custom"
    icon = "custom_components"

    def build_config(self):
        return {"param": {"display_name": "Parameter"}}

    def build(self, param: str) -> Record:
        return Record(data=param)
