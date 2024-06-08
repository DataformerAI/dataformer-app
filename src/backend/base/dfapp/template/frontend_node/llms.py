from typing import Optional

from dfapp.services.database.models.base import orjson_dumps
from dfapp.template.field.base import TemplateField
from dfapp.template.frontend_node.base import FrontendNode
from dfapp.template.frontend_node.constants import CTRANSFORMERS_DEFAULT_CONFIG, OPENAI_API_BASE_INFO


class LLMFrontendNode(FrontendNode):
    def add_extra_fields(self) -> None:
        if "VertexAI" in self.template.type_name:
            # Add credentials field which should of type file.
            self.template.add_field(
                TemplateField(
                    field_type="file",
                    required=False,
                    show=True,
                    name="credentials",
                    value="",
                    file_types=[".json"],
                )
            )

    @staticmethod
    def format_vertex_field(field: TemplateField, name: str):
        key = field.name or ""
        if "VertexAI" in name:
            advanced_fields = [
                "tuned_model_name",
                "verbose",
                "top_p",
                "top_k",
                "max_output_tokens",
            ]
            if key in advanced_fields:
                field.advanced = True
            show_fields = [
                "tuned_model_name",
                "verbose",
                "project",
                "location",
                "credentials",
                "max_output_tokens",
                "model_name",
                "temperature",
                "top_p",
                "top_k",
            ]

            if key in show_fields:
                field.show = True

    @staticmethod
    def format_openai_field(field: TemplateField):
        key = field.name or ""
        if "openai" in key.lower():
            field.display_name = (key.title().replace("Openai", "OpenAI").replace("_", " ")).replace("Api", "API")

        if "key" not in key.lower() and "token" not in key.lower():
            field.password = False

        if key == "openai_api_base":
            field.info = OPENAI_API_BASE_INFO

    def add_extra_base_classes(self) -> None:
        if "BaseLanguageModel" not in self.base_classes:
            self.base_classes.append("BaseLanguageModel")

    @staticmethod
    def format_azure_field(field: TemplateField):
        key = field.name or ""
        if key == "model_name":
            field.show = False  # Azure uses deployment_name instead of model_name.
        elif key == "openai_api_type":
            field.show = False
            field.password = False
            field.value = "azure"
        elif key == "openai_api_version":
            field.password = False

    @staticmethod
    def format_llama_field(field: TemplateField):
        field.show = True
        field.advanced = not field.required

    @staticmethod
    def format_ctransformers_field(field: TemplateField):
        key = field.name or ""
        if key == "config":
            field.show = True
            field.advanced = True
            field.value = orjson_dumps(CTRANSFORMERS_DEFAULT_CONFIG, indent_2=True)

    @staticmethod
    def format_field(field: TemplateField, name: Optional[str] = None) -> None:
        display_names_dict = {
            "huggingfacehub_api_token": "HuggingFace Hub API Token",
        }
        FrontendNode.format_field(field, name)
        LLMFrontendNode.format_openai_field(field)
        LLMFrontendNode.format_ctransformers_field(field)
        if name and "azure" in name.lower():
            LLMFrontendNode.format_azure_field(field)
        if name and "llama" in name.lower():
            LLMFrontendNode.format_llama_field(field)
        if name and "vertex" in name.lower():
            LLMFrontendNode.format_vertex_field(field, name)
        SHOW_FIELDS = ["repo_id"]
        key = field.name or ""
        if key in SHOW_FIELDS:
            field.show = True

        if "api" in key and ("key" in key or ("token" in key and "tokens" not in key)):
            field.password = True
            field.show = True
            # Required should be False to support
            # loading the API key from environment variables
            field.required = False
            field.advanced = False

        if key == "task":
            field.required = True
            field.show = True
            field.is_list = True
            field.options = ["text-generation", "text2text-generation", "summarization"]
            field.value = field.options[0]
            field.advanced = True

        if display_name := display_names_dict.get(key):
            field.display_name = display_name
        if key == "model_kwargs":
            field.field_type = "dict"
            field.advanced = True
            field.show = True
        elif key in [
            "model_name",
            "temperature",
            "model_file",
            "model_type",
            "deployment_name",
            "credentials",
        ]:
            field.advanced = False
            field.show = True
        if key == "credentials":
            field.field_type = "file"
        if name == "VertexAI" and key not in [
            "callbacks",
            "client",
            "stop",
            "tags",
            "cache",
        ]:
            field.show = True
