import { Edge, Node } from "reactflow";
import { FlowType, NodeType } from "../flow";

export type unselectAllNodesType = {
  updateNodes: (nodes: Node[]) => void;
  data: Node[];
};

export type updateEdgesHandleIdsType = {
  nodes: NodeType[];
  edges: Edge[];
};

export type generateFlowType = { newFlow: FlowType; removedEdges: Edge[] };

export type findLastNodeType = {
  nodes: NodeType[];
  edges: Edge[];
};
