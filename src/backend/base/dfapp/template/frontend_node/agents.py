from typing import Optional

from langchain.agents import types


from dfapp.template.field.base import TemplateField
from dfapp.template.frontend_node.base import FrontendNode
from dfapp.template.template.base import Template

NON_CHAT_AGENTS = {
    agent_type: agent_class
    for agent_type, agent_class in types.AGENT_TO_CLASS.items()
    if "chat" not in agent_type.value
}


class AgentFrontendNode(FrontendNode):
    @staticmethod
    def format_field(field: TemplateField, name: Optional[str] = None) -> None:
        if field.name in ["suffix", "prefix"]:
            field.show = True
        if field.name == "Tools" and name == "ZeroShotAgent":
            field.field_type = "BaseTool"
            field.is_list = True


class SQLAgentNode(FrontendNode):
    name: str = "SQLAgent"
    template: Template = Template(
        type_name="sql_agent",
        fields=[
            TemplateField(
                field_type="str",  # pyright: ignore
                required=True,
                placeholder="",
                is_list=False,  # pyright: ignore
                show=True,
                multiline=False,
                value="",
                name="database_uri",
            ),
            TemplateField(
                field_type="BaseLanguageModel",  # pyright: ignore
                required=True,
                show=True,
                name="llm",
                display_name="LLM",
            ),
        ],
    )
    description: str = """Construct an SQL agent from an LLM and tools."""
    base_classes: list[str] = ["AgentExecutor"]


class VectorStoreRouterAgentNode(FrontendNode):
    name: str = "VectorStoreRouterAgent"
    template: Template = Template(
        type_name="vectorstorerouter_agent",
        fields=[
            TemplateField(
                field_type="VectorStoreRouterToolkit",  # pyright: ignore
                required=True,
                show=True,
                name="vectorstoreroutertoolkit",
                display_name="Vector Store Router Toolkit",
            ),
            TemplateField(
                field_type="BaseLanguageModel",  # pyright: ignore
                required=True,
                show=True,
                name="llm",
                display_name="LLM",
            ),
        ],
    )
    description: str = """Construct an agent from a Vector Store Router."""
    base_classes: list[str] = ["AgentExecutor"]


class VectorStoreAgentNode(FrontendNode):
    name: str = "VectorStoreAgent"
    template: Template = Template(
        type_name="vectorstore_agent",
        fields=[
            TemplateField(
                field_type="VectorStoreInfo",  # pyright: ignore
                required=True,
                show=True,
                name="vectorstoreinfo",
                display_name="Vector Store Info",
            ),
            TemplateField(
                field_type="BaseLanguageModel",  # pyright: ignore
                required=True,
                show=True,
                name="llm",
                display_name="LLM",
            ),
        ],
    )
    description: str = """Construct an agent from a Vector Store."""
    base_classes: list[str] = ["AgentExecutor"]


class SQLDatabaseNode(FrontendNode):
    name: str = "SQLDatabase"
    template: Template = Template(
        type_name="sql_database",
        fields=[
            TemplateField(
                field_type="str",  # pyright: ignore
                required=True,
                is_list=False,  # pyright: ignore
                show=True,
                multiline=False,
                value="",
                name="uri",
            ),
        ],
    )
    description: str = """SQLAlchemy wrapper around a database."""
    base_classes: list[str] = ["SQLDatabase"]


class CSVAgentNode(FrontendNode):
    name: str = "CSVAgent"
    template: Template = Template(
        type_name="csv_agent",
        fields=[
            TemplateField(
                field_type="file",  # pyright: ignore
                required=True,
                show=True,
                name="path",
                value="",
                file_types=[".csv"],  # pyright: ignore
            ),
            TemplateField(
                field_type="BaseLanguageModel",  # pyright: ignore
                required=True,
                show=True,
                name="llm",
                display_name="LLM",
            ),
        ],
    )
    description: str = """Construct a CSV agent from a CSV and tools."""
    base_classes: list[str] = ["AgentExecutor"]


class JsonAgentNode(FrontendNode):
    name: str = "JsonAgent"
    template: Template = Template(
        type_name="json_agent",
        fields=[
            TemplateField(
                field_type="BaseToolkit",  # pyright: ignore
                required=True,
                show=True,
                name="toolkit",
            ),
            TemplateField(
                field_type="BaseLanguageModel",  # pyright: ignore
                required=True,
                show=True,
                name="llm",
                display_name="LLM",
            ),
        ],
    )
    description: str = """Construct a json agent from an LLM and tools."""
    base_classes: list[str] = ["AgentExecutor"]
