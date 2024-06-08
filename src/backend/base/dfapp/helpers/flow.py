from typing import TYPE_CHECKING, Any, Awaitable, Callable, List, Optional, Tuple, Type, Union, cast

from dfapp.schema.schema import INPUT_FIELD_NAME, Record
from dfapp.services.database.models.flow.model import Flow
from dfapp.services.deps import session_scope
from pydantic.v1 import BaseModel, Field, create_model
from sqlmodel import select

if TYPE_CHECKING:
    from dfapp.graph.graph.base import Graph
    from dfapp.graph.vertex.base import Vertex

INPUT_TYPE_MAP = {
    "ChatInput": {"type_hint": "Optional[str]", "default": '""'},
    "TextInput": {"type_hint": "Optional[str]", "default": '""'},
    "JSONInput": {"type_hint": "Optional[dict]", "default": "{}"},
}


def list_flows(*, user_id: Optional[str] = None) -> List[Record]:
    if not user_id:
        raise ValueError("Session is invalid")
    try:
        with session_scope() as session:
            flows = session.exec(
                select(Flow).where(Flow.user_id == user_id).where(Flow.is_component == False)  # noqa
            ).all()

            flows_records = [flow.to_record() for flow in flows]
            return flows_records
    except Exception as e:
        raise ValueError(f"Error listing flows: {e}")


async def load_flow(
    user_id: str, flow_id: Optional[str] = None, flow_name: Optional[str] = None, tweaks: Optional[dict] = None
) -> "Graph":
    from dfapp.graph.graph.base import Graph
    from dfapp.processing.process import process_tweaks

    if not flow_id and not flow_name:
        raise ValueError("Flow ID or Flow Name is required")
    if not flow_id and flow_name:
        flow_id = find_flow(flow_name, user_id)
        if not flow_id:
            raise ValueError(f"Flow {flow_name} not found")

    with session_scope() as session:
        graph_data = flow.data if (flow := session.get(Flow, flow_id)) else None
    if not graph_data:
        raise ValueError(f"Flow {flow_id} not found")
    if tweaks:
        graph_data = process_tweaks(graph_data=graph_data, tweaks=tweaks)
    graph = Graph.from_payload(graph_data, flow_id=flow_id)
    return graph


def find_flow(flow_name: str, user_id: str) -> Optional[str]:
    with session_scope() as session:
        flow = session.exec(select(Flow).where(Flow.name == flow_name).where(Flow.user_id == user_id)).first()
        return flow.id if flow else None


async def run_flow(
    inputs: Optional[Union[dict, List[dict]]] = None,
    tweaks: Optional[dict] = None,
    flow_id: Optional[str] = None,
    flow_name: Optional[str] = None,
    user_id: Optional[str] = None,
) -> Any:
    if user_id is None:
        raise ValueError("Session is invalid")
    graph = await load_flow(user_id, flow_id, flow_name, tweaks)

    if inputs is None:
        inputs = []
    inputs_list = []
    inputs_components = []
    types = []
    for input_dict in inputs:
        inputs_list.append({INPUT_FIELD_NAME: cast(str, input_dict.get("input_value"))})
        inputs_components.append(input_dict.get("components", []))
        types.append(input_dict.get("type", []))

    return await graph.arun(inputs_list, inputs_components=inputs_components, types=types)


def generate_function_for_flow(inputs: List["Vertex"], flow_id: str) -> Callable[..., Awaitable[Any]]:
    """
    Generate a dynamic flow function based on the given inputs and flow ID.

    Args:
        inputs (List[Vertex]): The list of input vertices for the flow.
        flow_id (str): The ID of the flow.

    Returns:
        Coroutine: The dynamic flow function.

    Raises:
        None

    Example:
        inputs = [vertex1, vertex2]
        flow_id = "my_flow"
        function = generate_function_for_flow(inputs, flow_id)
        result = function(input1, input2)
    """
    # Prepare function arguments with type hints and default values
    args = [
        f"{input_.display_name.lower().replace(' ', '_')}: {INPUT_TYPE_MAP[input_.base_name]['type_hint']} = {INPUT_TYPE_MAP[input_.base_name]['default']}"
        for input_ in inputs
    ]

    # Maintain original argument names for constructing the tweaks dictionary
    original_arg_names = [input_.display_name for input_ in inputs]

    # Prepare a Pythonic, valid function argument string
    func_args = ", ".join(args)

    # Map original argument names to their corresponding Pythonic variable names in the function
    arg_mappings = ", ".join(
        f'"{original_name}": {name}'
        for original_name, name in zip(original_arg_names, [arg.split(":")[0] for arg in args])
    )

    func_body = f"""
from typing import Optional
async def flow_function({func_args}):
    tweaks = {{ {arg_mappings} }}
    from dfapp.helpers.flow import run_flow
    from langchain_core.tools import ToolException
    try:
        return await run_flow(
            tweaks={{key: {{'input_value': value}} for key, value in tweaks.items()}},
            flow_id="{flow_id}",
        )
    except Exception as e:
        raise ToolException(f'Error running flow: ' + e)
"""

    compiled_func = compile(func_body, "<string>", "exec")
    local_scope: dict = {}
    exec(compiled_func, globals(), local_scope)
    return local_scope["flow_function"]


def build_function_and_schema(
    flow_record: Record, graph: "Graph"
) -> Tuple[Callable[..., Awaitable[Any]], Type[BaseModel]]:
    """
    Builds a dynamic function and schema for a given flow.

    Args:
        flow_record (Record): The flow record containing information about the flow.
        graph (Graph): The graph representing the flow.

    Returns:
        Tuple[Callable, BaseModel]: A tuple containing the dynamic function and the schema.
    """
    flow_id = flow_record.id
    inputs = get_flow_inputs(graph)
    dynamic_flow_function = generate_function_for_flow(inputs, flow_id)
    schema = build_schema_from_inputs(flow_record.name, inputs)
    return dynamic_flow_function, schema


def get_flow_inputs(graph: "Graph") -> List["Vertex"]:
    """
    Retrieves the flow inputs from the given graph.

    Args:
        graph (Graph): The graph object representing the flow.

    Returns:
        List[Record]: A list of input records, where each record contains the ID, name, and description of the input vertex.
    """
    inputs = []
    for vertex in graph.vertices:
        if vertex.is_input:
            inputs.append(vertex)
    return inputs


def build_schema_from_inputs(name: str, inputs: List["Vertex"]) -> Type[BaseModel]:
    """
    Builds a schema from the given inputs.

    Args:
        name (str): The name of the schema.
        inputs (List[tuple[str, str, str]]): A list of tuples representing the inputs.
            Each tuple contains three elements: the input name, the input type, and the input description.

    Returns:
        BaseModel: The schema model.

    """
    fields = {}
    for input_ in inputs:
        field_name = input_.display_name.lower().replace(" ", "_")
        description = input_.description
        fields[field_name] = (str, Field(default="", description=description))
    return create_model(name, **fields)  # type: ignore
