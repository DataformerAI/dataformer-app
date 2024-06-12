import {
  Connection,
  Edge,
  Node,
  OnEdgesChange,
  OnNodesChange,
  ReactFlowInstance,
  Viewport,
} from "reactflow";
import { BuildStatus } from "../../../constants/enums";
import { VertexBuildTypeAPI } from "../../api";
import { ChatInputType, ChatOutputType } from "../../chat";
import { FlowState } from "../../tabs";

export type FlowPoolObjectType = {
  timestamp: string;
  valid: boolean;
  messages: Array<ChatOutputType | ChatInputType> | [];
  data: {
    artifacts: any | ChatOutputType | ChatInputType;
    results: any | ChatOutputType | ChatInputType;
  };
  duration?: string;
  progress?: number;
  id: string;
  buildId: string;
};

export type FlowPoolObjectTypeNew = {
  //build
  //1 - error->logs
  //2 - success-> result
  timestamp: string;
  valid: boolean;
  data: {
    logs?: any | ChatOutputType | ChatInputType;
    results: any | ChatOutputType | ChatInputType;
  };
  duration?: string;
  progress?: number;
  //retrieve component type from id
  id: string;
  buildId: string;
};

export type VertexLayerElementType = {
  id: string;
  reference?: string;
};

export type FlowPoolType = {
  [key: string]: Array<VertexBuildTypeAPI>;
};

export type FlowStoreType = {
  onFlowPage: boolean;
  setOnFlowPage: (onFlowPage: boolean) => void;
  flowPool: FlowPoolType;
  inputs: Array<{
    type: string;
    id: string;
    displayName: string;
  }>;
  outputs: Array<{
    type: string;
    id: string;
    displayName: string;
  }>;
  hasIO: boolean;
  setFlowPool: (flowPool: FlowPoolType) => void;
  addDataToFlowPool: (data: VertexBuildTypeAPI, nodeId: string) => void;
  CleanFlowPool: () => void;
  isBuilding: boolean;
  isPending: boolean;
  setIsBuilding: (isBuilding: boolean) => void;
  setPending: (isPending: boolean) => void;
  resetFlow: (flow: {
    nodes: Node[];
    edges: Edge[];
    viewport: Viewport;
  }) => void;
  reactFlowInstance: ReactFlowInstance | null;
  setReactFlowInstance: (newState: ReactFlowInstance) => void;
  flowState: FlowState | undefined;
  setFlowState: (
    state:
      | FlowState
      | undefined
      | ((oldState: FlowState | undefined) => FlowState),
  ) => void;
  nodes: Node[];
  edges: Edge[];
  onNodesChange: OnNodesChange;
  onEdgesChange: OnEdgesChange;
  setNodes: (
    update: Node[] | ((oldState: Node[]) => Node[]),
    skipSave?: boolean,
  ) => void;
  setEdges: (
    update: Edge[] | ((oldState: Edge[]) => Edge[]),
    skipSave?: boolean,
  ) => void;
  setNode: (id: string, update: Node | ((oldState: Node) => Node)) => void;
  getNode: (id: string) => Node | undefined;
  deleteNode: (nodeId: string | Array<string>) => void;
  deleteEdge: (edgeId: string | Array<string>) => void;
  paste: (
    selection: { nodes: any; edges: any },
    position: { x: number; y: number; paneX?: number; paneY?: number },
  ) => void;
  lastCopiedSelection: { nodes: any; edges: any } | null;
  setLastCopiedSelection: (
    newSelection: { nodes: any; edges: any } | null,
    isCrop?: boolean,
  ) => void;
  cleanFlow: () => void;
  setFilterEdge: (newState) => void;
  getFilterEdge: any[];
  onConnect: (connection: Connection) => void;
  unselectAll: () => void;
  buildFlow: ({
    startNodeId,
    stopNodeId,
    input_value,
    files,
    silent,
  }: {
    startNodeId?: string;
    stopNodeId?: string;
    input_value?: string;
    files?: string[];
    silent?: boolean;
  }) => Promise<void>;
  getFlow: () => { nodes: Node[]; edges: Edge[]; viewport: Viewport };
  updateVerticesBuild: (
    vertices: {
      verticesIds: string[];
      verticesLayers: VertexLayerElementType[][];
      runId: string;
      verticesToRun: string[];
    } | null,
  ) => void;
  addToVerticesBuild: (vertices: string[]) => void;
  removeFromVerticesBuild: (vertices: string[]) => void;
  verticesBuild: {
    verticesIds: string[];
    verticesLayers: VertexLayerElementType[][];
    runId: string;
    verticesToRun: string[];
  } | null;
  updateBuildStatus: (nodeId: string[], status: BuildStatus) => void;
  revertBuiltStatusFromBuilding: () => void;
  flowBuildStatus: {
    [key: string]: { status: BuildStatus; timestamp?: string };
  };
  updateFlowPool: (
    nodeId: string,
    data: VertexBuildTypeAPI | ChatOutputType | ChatInputType,
    buildId?: string,
  ) => void;
  getNodePosition: (nodeId: string) => { x: number; y: number };
};
