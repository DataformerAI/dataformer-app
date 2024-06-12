import { cloneDeep, zip } from "lodash";
import {
  Edge,
  EdgeChange,
  Node,
  NodeChange,
  addEdge,
  applyEdgeChanges,
  applyNodeChanges,
} from "reactflow";
import { create } from "zustand";
import {
  FLOW_BUILD_SUCCESS_ALERT,
  MISSED_ERROR_ALERT,
} from "../constants/alerts_constants";
import { BuildStatus } from "../constants/enums";
import { getFlowPool } from "../controllers/API";
import { VertexBuildTypeAPI } from "../types/api";
import { ChatInputType, ChatOutputType } from "../types/chat";
import {
  NodeDataType,
  NodeType,
  sourceHandleType,
  targetHandleType,
} from "../types/flow";
import { FlowStoreType, VertexLayerElementType } from "../types/zustand/flow";
import { buildVertices } from "../utils/buildUtils";
import {
  checkChatInput,
  cleanEdges,
  getHandleId,
  getNodeId,
  scapeJSONParse,
  scapedJSONStringfy,
  updateGroupRecursion,
  validateNodes,
} from "../utils/reactflowUtils";
import { getInputsAndOutputs } from "../utils/storeUtils";
import useAlertStore from "./alertStore";
import { useDarkStore } from "./darkStore";
import useFlowsManagerStore from "./flowsManagerStore";

// this is our useStore hook that we can use in our components to get parts of the store and call actions
const useFlowStore = create<FlowStoreType>((set, get) => ({
  onFlowPage: false,
  setOnFlowPage: (FlowPage) => set({ onFlowPage: FlowPage }),
  flowState: undefined,
  flowBuildStatus: {},
  nodes: [],
  edges: [],
  isBuilding: false,
  isPending: true,
  hasIO: false,
  reactFlowInstance: null,
  lastCopiedSelection: null,
  flowPool: {},
  inputs: [],
  outputs: [],
  setFlowPool: (flowPool) => {
    set({ flowPool });
  },
  addDataToFlowPool: (data: VertexBuildTypeAPI, nodeId: string) => {
    let newFlowPool = cloneDeep({ ...get().flowPool });
    if (!newFlowPool[nodeId]) newFlowPool[nodeId] = [data];
    else {
      newFlowPool[nodeId].push(data);
    }
    get().setFlowPool(newFlowPool);
  },
  getNodePosition: (nodeId: string) => {
    const node = get().nodes.find((node) => node.id === nodeId);
    return node?.position || { x: 0, y: 0 };
  },
  updateFlowPool: (
    nodeId: string,
    data: VertexBuildTypeAPI | ChatOutputType | ChatInputType,
    buildId?: string,
  ) => {
    let newFlowPool = cloneDeep({ ...get().flowPool });
    if (!newFlowPool[nodeId]) {
      return;
    } else {
      let index = newFlowPool[nodeId].length - 1;
      if (buildId) {
        index = newFlowPool[nodeId].findIndex((flow) => flow.id === buildId);
      }
      //check if the data is a flowpool object
      if ((data as VertexBuildTypeAPI).valid !== undefined) {
        newFlowPool[nodeId][index] = data as VertexBuildTypeAPI;
      }
      //update data results
      else {
        newFlowPool[nodeId][index].data.message = data as
          | ChatOutputType
          | ChatInputType;
      }
    }
    get().setFlowPool(newFlowPool);
  },
  CleanFlowPool: () => {
    get().setFlowPool({});
  },
  setPending: (isPending) => {
    set({ isPending });
  },
  resetFlow: ({ nodes, edges, viewport }) => {
    const currentFlow = useFlowsManagerStore.getState().currentFlow;
    let newEdges = cleanEdges(nodes, edges);
    const { inputs, outputs } = getInputsAndOutputs(nodes);
    set({
      nodes,
      edges: newEdges,
      flowState: undefined,
      inputs,
      outputs,
      hasIO: inputs.length > 0 || outputs.length > 0,
    });
    get().reactFlowInstance!.setViewport(viewport);
    if (currentFlow) {
      getFlowPool({ flowId: currentFlow.id }).then((flowPool) => {
        set({ flowPool: flowPool.data.vertex_builds });
      });
    }
  },
  setIsBuilding: (isBuilding) => {
    set({ isBuilding });
  },
  setFlowState: (flowState) => {
    const newFlowState =
      typeof flowState === "function" ? flowState(get().flowState) : flowState;

    if (newFlowState !== get().flowState) {
      set(() => ({
        flowState: newFlowState,
      }));
    }
  },
  setReactFlowInstance: (newState) => {
    set({ reactFlowInstance: newState });
  },
  onNodesChange: (changes: NodeChange[]) => {
    set({
      nodes: applyNodeChanges(changes, get().nodes),
    });
  },
  onEdgesChange: (changes: EdgeChange[]) => {
    set({
      edges: applyEdgeChanges(changes, get().edges),
    });
  },
  setNodes: (change, skipSave = false) => {
    let newChange = typeof change === "function" ? change(get().nodes) : change;
    let newEdges = cleanEdges(newChange, get().edges);
    const { inputs, outputs } = getInputsAndOutputs(newChange);

    set({
      edges: newEdges,
      nodes: newChange,
      flowState: undefined,
      inputs,
      outputs,
      hasIO: inputs.length > 0 || outputs.length > 0,
    });

    const flowsManager = useFlowsManagerStore.getState();
    if (!get().isBuilding && !skipSave && get().onFlowPage) {
      flowsManager.autoSaveCurrentFlow(
        newChange,
        newEdges,
        get().reactFlowInstance?.getViewport() ?? { x: 0, y: 0, zoom: 1 },
      );
    }
  },
  setEdges: (change, skipSave = false) => {
    let newChange = typeof change === "function" ? change(get().edges) : change;
    set({
      edges: newChange,
      flowState: undefined,
    });

    const flowsManager = useFlowsManagerStore.getState();
    if (!get().isBuilding && !skipSave && get().onFlowPage) {
      flowsManager.autoSaveCurrentFlow(
        get().nodes,
        newChange,
        get().reactFlowInstance?.getViewport() ?? { x: 0, y: 0, zoom: 1 },
      );
    }
  },
  setNode: (id: string, change: Node | ((oldState: Node) => Node)) => {
    let newChange =
      typeof change === "function"
        ? change(get().nodes.find((node) => node.id === id)!)
        : change;
    get().setNodes((oldNodes) =>
      oldNodes.map((node) => {
        if (node.id === id) {
          if ((node.data as NodeDataType).node?.frozen) {
            (newChange.data as NodeDataType).node!.frozen = false;
          }
          return newChange;
        }
        return node;
      }),
    );
  },
  getNode: (id: string) => {
    return get().nodes.find((node) => node.id === id);
  },
  deleteNode: (nodeId) => {
    get().setNodes(
      get().nodes.filter((node) =>
        typeof nodeId === "string"
          ? node.id !== nodeId
          : !nodeId.includes(node.id),
      ),
    );
  },
  deleteEdge: (edgeId) => {
    get().setEdges(
      get().edges.filter((edge) =>
        typeof edgeId === "string"
          ? edge.id !== edgeId
          : !edgeId.includes(edge.id),
      ),
    );
  },
  paste: (selection, position) => {
    if (
      selection.nodes.some((node) => node.data.type === "ChatInput") &&
      checkChatInput(get().nodes)
    ) {
      useAlertStore.getState().setErrorData({
        title: "Error pasting components",
        list: ["You can only have one ChatInput component in the flow"],
      });
      return;
    }
    let minimumX = Infinity;
    let minimumY = Infinity;
    let idsMap = {};
    let newNodes: Node<NodeDataType>[] = get().nodes;
    let newEdges = get().edges;
    selection.nodes.forEach((node: Node) => {
      if (node.position.y < minimumY) {
        minimumY = node.position.y;
      }
      if (node.position.x < minimumX) {
        minimumX = node.position.x;
      }
    });

    const insidePosition = position.paneX
      ? { x: position.paneX + position.x, y: position.paneY! + position.y }
      : get().reactFlowInstance!.screenToFlowPosition({
          x: position.x,
          y: position.y,
        });

    selection.nodes.forEach((node: NodeType) => {
      // Generate a unique node ID
      let newId = getNodeId(node.data.type);
      idsMap[node.id] = newId;

      // Create a new node object
      const newNode: NodeType = {
        id: newId,
        type: "genericNode",
        position: {
          x: insidePosition.x + node.position!.x - minimumX,
          y: insidePosition.y + node.position!.y - minimumY,
        },
        data: {
          ...cloneDeep(node.data),
          id: newId,
        },
      };
      updateGroupRecursion(newNode, selection.edges);

      // Add the new node to the list of nodes in state
      newNodes = newNodes
        .map((node) => ({ ...node, selected: false }))
        .concat({ ...newNode, selected: false });
    });
    get().setNodes(newNodes);

    selection.edges.forEach((edge: Edge) => {
      let source = idsMap[edge.source];
      let target = idsMap[edge.target];
      const sourceHandleObject: sourceHandleType = scapeJSONParse(
        edge.sourceHandle!,
      );
      let sourceHandle = scapedJSONStringfy({
        ...sourceHandleObject,
        id: source,
      });
      sourceHandleObject.id = source;

      edge.data.sourceHandle = sourceHandleObject;
      const targetHandleObject: targetHandleType = scapeJSONParse(
        edge.targetHandle!,
      );
      let targetHandle = scapedJSONStringfy({
        ...targetHandleObject,
        id: target,
      });
      targetHandleObject.id = target;
      edge.data.targetHandle = targetHandleObject;
      let id = getHandleId(source, sourceHandle, target, targetHandle);
      newEdges = addEdge(
        {
          source,
          target,
          sourceHandle,
          targetHandle,
          id,
          data: cloneDeep(edge.data),
          selected: false,
        },
        newEdges.map((edge) => ({ ...edge, selected: false })),
      );
    });
    get().setEdges(newEdges);
  },
  setLastCopiedSelection: (newSelection, isCrop = false) => {
    if (isCrop) {
      const nodesIdsSelected = newSelection!.nodes.map((node) => node.id);
      const edgesIdsSelected = newSelection!.edges.map((edge) => edge.id);

      nodesIdsSelected.forEach((id) => {
        get().deleteNode(id);
      });

      edgesIdsSelected.forEach((id) => {
        get().deleteEdge(id);
      });

      const newNodes = get().nodes.filter(
        (node) => !nodesIdsSelected.includes(node.id),
      );
      const newEdges = get().edges.filter(
        (edge) => !edgesIdsSelected.includes(edge.id),
      );

      set({ nodes: newNodes, edges: newEdges });
    }

    set({ lastCopiedSelection: newSelection });
  },
  cleanFlow: () => {
    set({
      nodes: [],
      edges: [],
      flowState: undefined,
      getFilterEdge: [],
    });
  },
  setFilterEdge: (newState) => {
    set({ getFilterEdge: newState });
  },
  getFilterEdge: [],
  onConnect: (connection) => {
    const dark = useDarkStore.getState().dark;
    // const commonMarkerProps = {
    //   type: MarkerType.ArrowClosed,
    //   width: 20,
    //   height: 20,
    //   color: dark ? "#555555" : "#000000",
    // };

    // const inputTypes = INPUT_TYPES;
    // const outputTypes = OUTPUT_TYPES;

    // const findNode = useFlowStore
    //   .getState()
    //   .nodes.find(
    //     (node) => node.id === connection.source || node.id === connection.target
    //   );

    // const sourceType = findNode?.data?.type;
    // let isIoIn = false;
    // let isIoOut = false;
    // if (sourceType) {
    //   isIoIn = inputTypes.has(sourceType);
    //   isIoOut = outputTypes.has(sourceType);
    // }

    let newEdges: Edge[] = [];
    get().setEdges((oldEdges) => {
      newEdges = addEdge(
        {
          ...connection,
          data: {
            targetHandle: scapeJSONParse(connection.targetHandle!),
            sourceHandle: scapeJSONParse(connection.sourceHandle!),
          },
          // style: { stroke: "#555" },
          // className: "stroke-foreground stroke-connection",
        },
        oldEdges,
      );

      return newEdges;
    });
    useFlowsManagerStore
      .getState()
      .autoSaveCurrentFlow(
        get().nodes,
        newEdges,
        get().reactFlowInstance?.getViewport() ?? { x: 0, y: 0, zoom: 1 },
      );
  },
  unselectAll: () => {
    let newNodes = cloneDeep(get().nodes);
    newNodes.forEach((node) => {
      node.selected = false;
      let newEdges = cleanEdges(newNodes, get().edges);
      set({
        nodes: newNodes,
        edges: newEdges,
      });
    });
  },
  buildFlow: async ({
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
  }) => {
    get().setIsBuilding(true);
    const currentFlow = useFlowsManagerStore.getState().currentFlow;
    const setSuccessData = useAlertStore.getState().setSuccessData;
    const setErrorData = useAlertStore.getState().setErrorData;
    const setNoticeData = useAlertStore.getState().setNoticeData;
    function validateSubgraph(nodes: string[]) {
      const errorsObjs = validateNodes(
        get().nodes.filter((node) => nodes.includes(node.id)),
        get().edges,
      );

      const errors = errorsObjs.map((obj) => obj.errors).flat();
      if (errors.length > 0) {
        setErrorData({
          title: MISSED_ERROR_ALERT,
          list: errors,
        });
        get().setIsBuilding(false);
        const ids = errorsObjs.map((obj) => obj.id).flat();

        get().updateBuildStatus(ids, BuildStatus.ERROR);
        throw new Error("Invalid nodes");
      }
    }
    function handleBuildUpdate(
      vertexBuildData: VertexBuildTypeAPI,
      status: BuildStatus,
      runId: string,
    ) {
      if (vertexBuildData && vertexBuildData.inactivated_vertices) {
        get().removeFromVerticesBuild(vertexBuildData.inactivated_vertices);
        get().updateBuildStatus(
          vertexBuildData.inactivated_vertices,
          BuildStatus.INACTIVE,
        );
      }

      if (vertexBuildData.next_vertices_ids) {
        // next_vertices_ids is a list of vertices that are going to be built next
        // verticesLayers is a list of list of vertices ids, where each list is a layer of vertices
        // we want to add a new layer (next_vertices_ids) to the list of layers (verticesLayers)
        // and the values of next_vertices_ids to the list of vertices ids (verticesIds)

        // const nextVertices will be the zip of vertexBuildData.next_vertices_ids and
        // vertexBuildData.top_level_vertices
        // the VertexLayerElementType as {id: next_vertices_id, layer: top_level_vertex}

        // next_vertices_ids should be next_vertices_ids without the inactivated vertices
        const next_vertices_ids = vertexBuildData.next_vertices_ids.filter(
          (id) => !vertexBuildData.inactivated_vertices?.includes(id),
        );
        const top_level_vertices = vertexBuildData.top_level_vertices.filter(
          (vertex) => !vertexBuildData.inactivated_vertices?.includes(vertex),
        );
        const nextVertices: VertexLayerElementType[] = zip(
          next_vertices_ids,
          top_level_vertices,
        ).map(([id, reference]) => ({ id: id!, reference }));

        const newLayers = [
          ...get().verticesBuild!.verticesLayers,
          nextVertices,
        ];
        const newIds = [
          ...get().verticesBuild!.verticesIds,
          ...next_vertices_ids,
        ];
        get().updateVerticesBuild({
          verticesIds: newIds,
          verticesLayers: newLayers,
          runId: runId,
          verticesToRun: get().verticesBuild!.verticesToRun,
        });
        get().updateBuildStatus(top_level_vertices, BuildStatus.TO_BUILD);
      }

      get().addDataToFlowPool(
        { ...vertexBuildData, run_id: runId },
        vertexBuildData.id,
      );

      useFlowStore.getState().updateBuildStatus([vertexBuildData.id], status);

      const verticesIds = get().verticesBuild?.verticesIds;
      const newFlowBuildStatus = { ...get().flowBuildStatus };
      // filter out the vertices that are not status
      const verticesToUpdate = verticesIds?.filter(
        (id) => newFlowBuildStatus[id]?.status !== BuildStatus.BUILT,
      );

      if (verticesToUpdate) {
        useFlowStore.getState().updateBuildStatus(verticesToUpdate, status);
      }
    }
    await buildVertices({
      input_value,
      files,
      flowId: currentFlow!.id,
      startNodeId,
      stopNodeId,
      onGetOrderSuccess: () => {
        if (!silent) {
          setNoticeData({ title: "Running components" });
        }
      },
      onBuildComplete: (allNodesValid) => {
        const nodeId = startNodeId || stopNodeId;
        if (!silent) {
          if (nodeId && allNodesValid) {
            setSuccessData({
              title: `${
                get().nodes.find((node) => node.id === nodeId)?.data.node
                  ?.display_name
              } built successfully`,
            });
          } else {
            setSuccessData({ title: FLOW_BUILD_SUCCESS_ALERT });
          }
        }
        get().setIsBuilding(false);
      },
      onBuildUpdate: handleBuildUpdate,
      onBuildError: (title: string, list: string[], elementList) => {
        const idList = elementList
          .map((element) => element.id)
          .filter(Boolean) as string[];
        useFlowStore.getState().updateBuildStatus(idList, BuildStatus.BUILT);
        setErrorData({ list, title });
        get().setIsBuilding(false);
      },
      onBuildStart: (elementList) => {
        const idList = elementList
          // reference is the id of the vertex or the id of the parent in a group node
          .map((element) => element.reference)
          .filter(Boolean) as string[];
        useFlowStore.getState().updateBuildStatus(idList, BuildStatus.BUILDING);
      },
      onValidateNodes: validateSubgraph,
      nodes: !get().onFlowPage ? get().nodes : undefined,
      edges: !get().onFlowPage ? get().edges : undefined,
    });
    get().setIsBuilding(false);
    get().revertBuiltStatusFromBuilding();
  },
  getFlow: () => {
    return {
      nodes: get().nodes,
      edges: get().edges,
      viewport: get().reactFlowInstance?.getViewport()!,
    };
  },
  updateVerticesBuild: (
    vertices: {
      verticesIds: string[];
      verticesLayers: VertexLayerElementType[][];
      runId: string;
      verticesToRun: string[];
    } | null,
  ) => {
    set({ verticesBuild: vertices });
  },
  verticesBuild: null,
  addToVerticesBuild: (vertices: string[]) => {
    const verticesBuild = get().verticesBuild;
    if (!verticesBuild) return;
    set({
      verticesBuild: {
        ...verticesBuild,
        verticesIds: [...verticesBuild.verticesIds, ...vertices],
      },
    });
  },
  removeFromVerticesBuild: (vertices: string[]) => {
    const verticesBuild = get().verticesBuild;
    if (!verticesBuild) return;
    set({
      verticesBuild: {
        ...verticesBuild,
        // remove the vertices from the list of vertices ids
        // that are going to be built
        verticesIds: get().verticesBuild!.verticesIds.filter(
          // keep the vertices that are not in the list of vertices to remove
          (vertex) => !vertices.includes(vertex),
        ),
      },
    });
  },
  updateBuildStatus: (nodeIdList: string[], status: BuildStatus) => {
    const newFlowBuildStatus = { ...get().flowBuildStatus };
    nodeIdList.forEach((id) => {
      newFlowBuildStatus[id] = {
        status,
      };
      if (status == BuildStatus.BUILT) {
        const timestamp_string = new Date(Date.now()).toLocaleString();
        newFlowBuildStatus[id].timestamp = timestamp_string;
      }
    });
    set({ flowBuildStatus: newFlowBuildStatus });
  },
  revertBuiltStatusFromBuilding: () => {
    const newFlowBuildStatus = { ...get().flowBuildStatus };
    Object.keys(newFlowBuildStatus).forEach((id) => {
      if (newFlowBuildStatus[id].status === BuildStatus.BUILDING) {
        newFlowBuildStatus[id].status = BuildStatus.BUILT;
      }
    });
  },
}));

export default useFlowStore;
