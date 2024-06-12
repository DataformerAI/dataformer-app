from dfapp.custom import CustomComponent
import json

class TextToJsonComponent(CustomComponent):
    display_name = "Text to Json"
    description = "Convert Json data from string data type to Json data type"
    icon = "merge"

    def build_config(self):
        return {
            "text": {
                "display_name": "Input Text",
                "info": "The Json data in string data type",
                "required": True,
            }
        }

    def build(self, text: str) -> list:
        text = text.split("```")[1]
        text = text.replace("`", "").strip()
        json_data = json.loads(text)
        return json_data
