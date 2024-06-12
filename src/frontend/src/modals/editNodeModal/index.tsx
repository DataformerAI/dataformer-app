import { ColDef, GridApi } from "ag-grid-community";
import { forwardRef, useEffect, useRef, useState } from "react";
import IconComponent from "../../components/genericIconComponent";
import TableComponent from "../../components/tableComponent";
import { Badge } from "../../components/ui/badge";
import { useDarkStore } from "../../stores/darkStore";
import useFlowStore from "../../stores/flowStore";
import { NodeDataType } from "../../types/flow";
import BaseModal from "../baseModal";
import useColumnDefs from "./hooks/use-column-defs";
import useRowData from "./hooks/use-row-data";
import { cloneDeep } from "lodash";

const EditNodeModal = forwardRef(
  (
    {
      nodeLength,
      open,
      setOpen,
      //      setOpenWDoubleClick,
      data,
    }: {
      nodeLength: number;
      open: boolean;
      setOpen: (open: boolean) => void;
      //      setOpenWDoubleClick: (open: boolean) => void;
      data: NodeDataType;
    },
    ref,
  ) => {
    const myData = useRef(cloneDeep(data));

    const isDark = useDarkStore((state) => state.dark);

    const setNode = useFlowStore((state) => state.setNode);

    function changeAdvanced(n) {
      myData.current.node!.template[n].advanced =
        !myData.current.node!.template[n]?.advanced;
    }

    const handleOnNewValue = (newValue: any, key: string) => {
      myData.current.node!.template[key].value = newValue;
    };

    const handleOnChangeDb = (newValue: boolean, key: string) => {
      myData.current.node!.template[key].load_from_db = newValue;
    };

    const rowData = useRowData(data, open);

    const columnDefs: ColDef[] = useColumnDefs(
      data,
      handleOnNewValue,
      handleOnChangeDb,
      changeAdvanced,
      open,
    );

    const [gridApi, setGridApi] = useState<GridApi | null>(null);

    useEffect(() => {
      if (gridApi && open) {
        myData.current = cloneDeep(data);
        gridApi.refreshCells();
      }
    }, [gridApi, open]);

    //    useEffect(() => {
    //      return () => {
    //        setOpenWDoubleClick(false);
    //      };
    //    }, []);

    return (
      <BaseModal key={data.id} open={open} setOpen={setOpen}>
        <BaseModal.Trigger>
          <></>
        </BaseModal.Trigger>
        <BaseModal.Header description={data.node?.description!}>
          <span className="pr-2">{data.type}</span>
          <Badge variant={isDark ? "gray" : "secondary"}>
            <span className="relative top-[0.6px]">ID: {data.id}</span>
          </Badge>
        </BaseModal.Header>
        <BaseModal.Content>
          <div className="flex h-full flex-col">
            <div className="h-full">
              {nodeLength > 0 && (
                <TableComponent
                  key={"editNode"}
                  onGridReady={(params) => {
                    setGridApi(params.api);
                  }}
                  tooltipShowDelay={0.5}
                  columnDefs={columnDefs}
                  rowData={rowData}
                />
              )}
            </div>
          </div>
        </BaseModal.Content>

        <BaseModal.Footer
          submit={{
            label: "Save Changes",
            onClick: () => {
              setNode(data.id, (old) => ({
                ...old,
                data: {
                  ...old.data,
                  node: myData.current.node,
                },
              }));
              setOpen(false);
            },
          }}
        />
      </BaseModal>
    );
  },
);

export default EditNodeModal;
