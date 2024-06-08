from collections import deque
import copy


def find_last_node(nodes, edges):
    """
    This function receives a flow and returns the last node.
    """
    return next((n for n in nodes if all(e["source"] != n["id"] for e in edges)), None)


def add_parent_node_id(nodes, parent_node_id):
    """
    This function receives a list of nodes and adds a parent_node_id to each node.
    """
    for node in nodes:
        node["parent_node_id"] = parent_node_id


def ungroup_node(group_node_data, base_flow):
    template, flow = (
        group_node_data["node"]["template"],
        group_node_data["node"]["flow"],
    )
    parent_node_id = group_node_data["id"]
    g_nodes = flow["data"]["nodes"]
    add_parent_node_id(g_nodes, parent_node_id)
    g_edges = flow["data"]["edges"]

    # Redirect edges to the correct proxy node
    updated_edges = get_updated_edges(base_flow, g_nodes, g_edges, group_node_data["id"])

    # Update template values
    update_template(template, g_nodes)

    nodes = [n for n in base_flow["nodes"] if n["id"] != group_node_data["id"]] + g_nodes
    edges = (
        [e for e in base_flow["edges"] if e["target"] != group_node_data["id"] and e["source"] != group_node_data["id"]]
        + g_edges
        + updated_edges
    )

    base_flow["nodes"] = nodes
    base_flow["edges"] = edges

    return nodes


def process_flow(flow_object):
    cloned_flow = copy.deepcopy(flow_object)
    processed_nodes = set()  # To keep track of processed nodes

    def process_node(node):
        node_id = node.get("id")

        # If node already processed, skip
        if node_id in processed_nodes:
            return

        if node.get("data") and node["data"].get("node") and node["data"]["node"].get("flow"):
            process_flow(node["data"]["node"]["flow"]["data"])
            new_nodes = ungroup_node(node["data"], cloned_flow)
            # Add new nodes to the queue for future processing
            nodes_to_process.extend(new_nodes)

        # Mark node as processed
        processed_nodes.add(node_id)

    nodes_to_process = deque(cloned_flow["nodes"])

    while nodes_to_process:
        node = nodes_to_process.popleft()
        process_node(node)

    return cloned_flow


def update_template(template, g_nodes):
    """
    Updates the template of a node in a graph with the given template.

    Args:
        template (dict): The new template to update the node with.
        g_nodes (list): The list of nodes in the graph.

    Returns:
        None
    """
    for _, value in template.items():
        if not value.get("proxy"):
            continue
        proxy_dict = value["proxy"]
        field, id_ = proxy_dict["field"], proxy_dict["id"]
        node_index = next((i for i, n in enumerate(g_nodes) if n["id"] == id_), -1)
        if node_index != -1:
            display_name = None
            show = g_nodes[node_index]["data"]["node"]["template"][field]["show"]
            advanced = g_nodes[node_index]["data"]["node"]["template"][field]["advanced"]
            if "display_name" in g_nodes[node_index]["data"]["node"]["template"][field]:
                display_name = g_nodes[node_index]["data"]["node"]["template"][field]["display_name"]
            else:
                display_name = g_nodes[node_index]["data"]["node"]["template"][field]["name"]

            g_nodes[node_index]["data"]["node"]["template"][field] = value
            g_nodes[node_index]["data"]["node"]["template"][field]["show"] = show
            g_nodes[node_index]["data"]["node"]["template"][field]["advanced"] = advanced
            g_nodes[node_index]["data"]["node"]["template"][field]["display_name"] = display_name


def update_target_handle(new_edge, g_nodes, group_node_id):
    """
    Updates the target handle of a given edge if it is a proxy node.

    Args:
        new_edge (dict): The edge to update.
        g_nodes (list): The list of nodes in the graph.
        group_node_id (str): The ID of the group node.

    Returns:
        dict: The updated edge.
    """
    target_handle = new_edge["data"]["targetHandle"]
    if target_handle.get("proxy"):
        proxy_id = target_handle["proxy"]["id"]
        if node := next((n for n in g_nodes if n["id"] == proxy_id), None):
            set_new_target_handle(proxy_id, new_edge, target_handle, node)
    return new_edge


def set_new_target_handle(proxy_id, new_edge, target_handle, node):
    """
    Sets a new target handle for a given edge.

    Args:
        proxy_id (str): The ID of the proxy.
        new_edge (dict): The new edge to be created.
        target_handle (dict): The target handle of the edge.
        node (dict): The node containing the edge.

    Returns:
        None
    """
    new_edge["target"] = proxy_id
    _type = target_handle.get("type")
    if _type is None:
        raise KeyError("The 'type' key must be present in target_handle.")

    field = target_handle["proxy"]["field"]
    new_target_handle = {
        "fieldName": field,
        "type": _type,
        "id": proxy_id,
    }
    if node["data"]["node"].get("flow"):
        new_target_handle["proxy"] = {
            "field": node["data"]["node"]["template"][field]["proxy"]["field"],
            "id": node["data"]["node"]["template"][field]["proxy"]["id"],
        }
    if input_types := target_handle.get("inputTypes"):
        new_target_handle["inputTypes"] = input_types
    new_edge["data"]["targetHandle"] = new_target_handle


def update_source_handle(new_edge, g_nodes, g_edges):
    """
    Updates the source handle of a given edge to the last node in the flow data.

    Args:
        new_edge (dict): The edge to update.
        flow_data (dict): The flow data containing the nodes and edges.

    Returns:
        dict: The updated edge with the new source handle.
    """
    last_node = copy.deepcopy(find_last_node(g_nodes, g_edges))
    new_edge["source"] = last_node["id"]
    new_source_handle = new_edge["data"]["sourceHandle"]
    new_source_handle["id"] = last_node["id"]
    new_edge["data"]["sourceHandle"] = new_source_handle
    return new_edge


def get_updated_edges(base_flow, g_nodes, g_edges, group_node_id):
    """
    Given a base flow, a list of graph nodes and a group node id, returns a list of updated edges.
    An updated edge is an edge that has its target or source handle updated based on the group node id.

    Args:
        base_flow (dict): The base flow containing a list of edges.
        g_nodes (list): A list of graph nodes.
        group_node_id (str): The id of the group node.

    Returns:
        list: A list of updated edges.
    """
    updated_edges = []
    for edge in base_flow["edges"]:
        new_edge = copy.deepcopy(edge)
        if new_edge["target"] == group_node_id:
            new_edge = update_target_handle(new_edge, g_nodes, group_node_id)

        if new_edge["source"] == group_node_id:
            new_edge = update_source_handle(new_edge, g_nodes, g_edges)

        if edge["target"] == group_node_id or edge["source"] == group_node_id:
            updated_edges.append(new_edge)
    return updated_edges
